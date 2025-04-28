import wave
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from src.media.base import Media
from src.kwargs import validate_kwargs
from src.tools import ProgressBar
from src.noise.none import NoNoiseGenerator
from og_log import LOG

class AudioWav(Media):
    VALID_CHANNELS = "123456789ABCDEF"

    @validate_kwargs({ 'mandatory': ['file'], 'optional': [{ 'name': 'summary', 'default': False }] })
    def __init__(self, **kwargs):
        self.filename = kwargs.pop('file')
        self.summary = kwargs.pop('summary')

        with wave.open(self.filename, 'rb') as wav:
            self.params = wav.getparams()
            self.frames = wav.readframes(wav.getnframes())

        # Convert to numpy array for easier manipulation
        self.sample_width = self.params.sampwidth
        if self.sample_width not in [1, 2]: raise Exception("Only 8-bit and 16-bit audio supported")
        self.n_channels = self.params.nchannels
        if self.n_channels > 16: raise Exception("More than 16 channels not supported")
        self.frame_rate = self.params.framerate
        self.n_frames = self.params.nframes

        dtype = np.int16 if self.sample_width == 2 else np.uint8  # Add more cases as needed
        self.audio_np = np.frombuffer(self.frames, dtype=dtype).copy()

        super().__init__(**kwargs)

    @property
    def tobytes_for_hash(self):
        masked_array = self.audio_np & (~0b111)
        return masked_array.tobytes()    

    @property
    def get_bit_count(self):
        print(len(self.audio_np) * self.sample_width * 8)
        return len(self.audio_np) * self.sample_width * 8
    
    def validate_pattern(self, pattern):
        valid = AudioWav.VALID_CHANNELS[:self.n_channels]  # 16 channel max
        count = Counter(pattern)
        is_valid = (
            all(char in valid for char in pattern) and
            all(count[char] == 1 for char in pattern) 
        )
        if not is_valid: raise Exception("Invalid WAV pattern")


    def generate_lsb_encoding_pattern(self, nbit: int, pattern: str):
        if not (1 <= nbit <= 3):
            raise Exception("nbit must be between 1 and 3")

        pattern = pattern.upper()
        valid_channels = AudioWav.VALID_CHANNELS[:self.n_channels]  # 16 channel max
        if not all(c in valid_channels for c in pattern):
            raise Exception("pattern must only contains " + valid_channels)
        
        channel_order = {ch: i for i, ch in enumerate(valid_channels)}
        pixel_bitfield = [0] * self.n_channels * self.sample_width * 8

        bit_index = 1
        for ch in pattern:
            channel_start = channel_order[ch] * self.sample_width * 8
            for i in range(nbit):
                pixel_bitfield[channel_start + i] = bit_index
                bit_index += 1

        return pixel_bitfield


    def entropy(self, salt: str) -> str:
        return hashlib.sha256(self.tobytes_for_hash + salt.encode("utf-8")).hexdigest()

    def encode(self, algo, codec, dispersion, noise):
        LOG.info(f"Encoding with {algo.__class__.__name__} and {codec.__class__.__name__} codec")
        LOG.info(f"Data to encode : {codec.output}")

        audio = self.audio_np.copy()
        o = dispersion.start_offset
        i = 0

        bit_pattern = algo.encoding_pattern
        pattern_bit_count = len(bit_pattern) - bit_pattern.count(0)
        offsets_status = [False] * algo.get_coding_bit_count()

        channel_bit_width = self.sample_width * 8

        max_idx = 0
        max_offset = 0

        pb = ProgressBar("Encoding secret : ", 0, len(codec.output))
        while i < len(codec.output):
            pb.update(i)
            pattern_value = o % pattern_bit_count + 1
            pos = bit_pattern.index(pattern_value)
            index = self.n_channels * ((o - (o % pattern_bit_count)) // pattern_bit_count) + pos // channel_bit_width 
            bit = pos % channel_bit_width

            sample = audio[index]
            audio[index] = (sample & ~(1 << bit)) | ((int(codec.output[i]) & 1) << bit)

            max_idx = max(max_idx, index)
            max_offset = max(max_offset, o)

            offsets_status[o] = True
            o = dispersion.inc_offset(o)
            i += 1
        pb.end()

        if type(noise) != NoNoiseGenerator:
            pb = ProgressBar("Adding noise : ", 0, len(offsets_status))
            for i in range(len(offsets_status)):
                pb.update(i)
                if offsets_status[i]: continue

                pattern_value = i % pattern_bit_count + 1
                pos = bit_pattern.index(pattern_value)
                index = self.n_channels * ((i - (i % pattern_bit_count)) // pattern_bit_count) + pos // channel_bit_width
                bit = pos % channel_bit_width

                sample = audio[index]
                n = noise.get((sample >> bit) & 1)
                if n is not None:
                    audio[index] = (sample & ~(1 << bit)) | ((n & 1) << bit)
            pb.end()

        if self.summary:
            print("Summary windows opened")
            self.show_summary(audio)
            print("Summary windows closed")

        return audio

    def decode(self, algo, codec, dispersion):
        LOG.info(f"Decoding with {algo.__class__.__name__} and {codec.__class__.__name__} codec")

        o = dispersion.start_offset
        data = ""

        bit_pattern = algo.encoding_pattern
        pattern_bit_count = len(bit_pattern) - bit_pattern.count(0)

        length = None
        pb = None

        channel_bit_width = self.sample_width * 8

        while length is None or len(data) < length:
            if length is None:
                f, val = codec.extract_size(data)
                if f:
                    LOG.info(f"Data size found: {val}")
                    length = val + len(data)
                    pb = ProgressBar("Decoding secret : ", len(data), length)

            pattern_value = o % pattern_bit_count + 1
            pos = bit_pattern.index(pattern_value)
            index = self.n_channels * ((o - (o % pattern_bit_count)) // pattern_bit_count) + pos // channel_bit_width
            bit = pos % channel_bit_width

            sample = self.audio_np[index]
            val = (sample >> bit) & 1
            data += str(val)

            if pb is not None: pb.update(len(data))
            o = dispersion.inc_offset(o)

        if pb is not None: pb.end()

        codec.decode(data)
        secret = codec.input
        LOG.info(f"Decoded data : {data}")
        return secret

    def save(self, output_filename, output):
        with wave.open(output_filename, 'wb') as out:
            out.setparams(self.params)
            out.writeframes(output.tobytes())

    def show_summary(self, modified_array=None):
        duration = self.n_frames / self.frame_rate
        time_axis = np.linspace(0, duration, num=self.audio_np.shape[0])

        fig, axs = plt.subplots(2 if modified_array is None else 3, 1, figsize=(24, 6), sharex=True)
        fig.suptitle(f"Waveform Summary: {self.filename}", fontsize=14)

        axs[0].plot(time_axis, self.audio_np, color='blue', label='Original')
        axs[0].set_title("Original Audio")
        axs[0].set_ylabel("Amplitude")
        axs[0].legend()

        if modified_array is not None:
            axs[1].plot(time_axis, modified_array, color='green', label='Modified')
            axs[1].set_title("Modified Audio")
            axs[1].set_ylabel("Amplitude")
            axs[1].legend()

            diff = np.abs(self.audio_np.astype(np.int32) - modified_array.astype(np.int32))
            axs[2].plot(time_axis, diff, color='red', label='Difference')
            axs[2].set_title("Difference (|Original - Modified|)")
            axs[2].set_xlabel("Time (s)")
            axs[2].set_ylabel("Δ Amplitude")
            axs[2].legend()
        else:
            axs[1].set_xlabel("Time (s)")

        plt.tight_layout()
        plt.show()
