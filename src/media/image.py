import hashlib
import PIL.Image, PIL.ImageChops
import matplotlib.pyplot as plt
import numpy as np

from src.media.base import Media
from src.kwargs import validate_kwargs
from src.tools import ProgressBar
from og_log import LOG

class Image(Media):
    CHANNEL_BIT_SIZE = 8
    CHANNEL_COUNT = 4
    PIXEL_BIT_SIZE = CHANNEL_COUNT * CHANNEL_BIT_SIZE

    @property
    def tobytes_for_hash(self):
        cleaned_pixels = [ (r & 0b11111000, g & 0b11111000, b & 0b11111000, a & 0b11111000) for r, g, b, a in self.media.getdata() ]
        cleaned_img = PIL.Image.new("RGBA", self.media.size)
        cleaned_img.putdata(cleaned_pixels)
        return cleaned_img.tobytes()

    @property
    def get_bit_count(self): return self.media.size[0] * self.media.size[1] * Image.PIXEL_BIT_SIZE

    def entropy(self,salt: str) -> str:
        return hashlib.sha256(self.tobytes_for_hash + salt.encode("utf-8")).hexdigest()

    @validate_kwargs({ 'mandatory': ['file'], 'optional': [{ 'name': 'summary', 'default': False }] })
    def __init__(self,**kwargs):
        self.filename = kwargs.pop('file')
        self.summary = kwargs.pop('summary')
        self.media = PIL.Image.open(self.filename).convert("RGBA")
        super().__init__(**kwargs)

    @staticmethod
    def Generate_bit_pattern(nbit: int, pattern: str):
        if not (1 <= nbit <= 3):
            raise ValueError("nbit must be between 1 and 3")

        pattern = pattern.upper()
        valid_channels = "RGBA"
        if not all(c in valid_channels for c in pattern):
            raise ValueError("pattern must only contain R, G, B, A")
        
        channel_order = {ch: i for i, ch in enumerate("RGBA")}
        pixel_bitfield = [0] * Image.PIXEL_BIT_SIZE  

        bit_index = 1
        for ch in pattern:
            channel_start = channel_order[ch] * Image.CHANNEL_BIT_SIZE
            for i in range(nbit):
                pixel_bitfield[channel_start + i] = bit_index
                bit_index += 1

        return pixel_bitfield

    def encode(self, algo, codec, dispersion, noise):
        tmp = self.media.copy()

        LOG.info(f"Encoding with {algo.__class__.__name__} and {codec.__class__.__name__} codec")
        LOG.info(f"Data to encode : {codec.output}")

        xmax,ymax = self.media.size
        pattern_coding_bits_count = len(algo.encoding_pattern) - algo.encoding_pattern.count(0)

        o = dispersion.start_offset
        i = 0

        offsets_status = [ False ] * algo.get_coding_bit_count(self)

        pb = ProgressBar("Encoding secret : ",0,len(codec.output))

        while i < len(codec.output):
            pb.update(i)

            pattern_value = o % pattern_coding_bits_count + 1
            pixel_index = (o - (o % pattern_coding_bits_count))//pattern_coding_bits_count
            x = pixel_index % xmax
            y = pixel_index // xmax
            pos = algo.encoding_pattern.index(pattern_value)
            bit = pos % Image.CHANNEL_BIT_SIZE
            channel = pos // Image.CHANNEL_BIT_SIZE
            r, g, b, a = tmp.getpixel((x, y))
            c = [r, g, b, a]

            c[channel] = (c[channel] & ~(1 << bit)) | ((int(codec.output[i]) & 1) << bit)
            tmp.putpixel((x, y), (c[0], c[1], c[2], c[3]))

            offsets_status[o] = True
            o = dispersion.inc_offset(o)
            i += 1

        pb.end()

        output = tmp.copy()

        pb = ProgressBar("Adding noise : ", 0, len(offsets_status))

        for i in range(len(offsets_status)):
            pb.update(i)

            if offsets_status[i]:
                continue

            pattern_value = i % pattern_coding_bits_count + 1
            pixel_index = (i - (i % pattern_coding_bits_count))//pattern_coding_bits_count
            x = pixel_index % xmax
            y = pixel_index // xmax
            pos = algo.encoding_pattern.index(pattern_value)
            bit = pos % Image.CHANNEL_BIT_SIZE
            channel = pos // Image.CHANNEL_BIT_SIZE
            r, g, b, a = output.getpixel((x, y))
            c = [r, g, b, a]

            n = noise.get((c[channel] >> bit) & 1)
            if n is not None:
                c[channel] = (c[channel] & ~(1 << bit)) | ((n & 1) << bit)
                output.putpixel((x, y), (c[0], c[1], c[2], c[3]))

        pb.end()

        if self.summary:
            print("Summary windows opened")
            self.show_summary(self.media,tmp,output)
            print("Summary windows closed")

        return output


    def decode(self, algo, codec, dispersion):
        LOG.info(f"Decoding with {algo.__class__.__name__} and {codec.__class__.__name__} codec")

        o = dispersion.start_offset

        data = ""

        xmax,ymax = self.media.size
        pattern_coding_bits_count = len(algo.encoding_pattern) - algo.encoding_pattern.count(0)

        length = None
        pb = None

        while length is None or len(data) < length:

            if length is None:
                f,val = codec.extract_size(data)
                if f:
                    LOG.info(f"Data size found: {val}")
                    length = val + len(data)
                    pb = ProgressBar("Decoding secret : ",len(data),length)

            pattern_value = o % pattern_coding_bits_count + 1
            pixel_index = (o - (o % pattern_coding_bits_count))//pattern_coding_bits_count
            x = pixel_index % xmax
            y = pixel_index // xmax
            pos = algo.encoding_pattern.index(pattern_value)
            bit = pos % Image.CHANNEL_BIT_SIZE
            channel = pos // Image.CHANNEL_BIT_SIZE
            r, g, b, a = self.media.getpixel((x, y))
            c = [r, g, b, a]

            val = (c[channel] >> bit) & 1
            data += str(val)

            if pb is not None: pb.update(len(data))

            o = dispersion.inc_offset(o)

        if pb is not None: pb.end()

        codec.decode(data)
        secret = codec.input

        LOG.info(f"Decoded data : {data}")

        return secret



    def show_summary(self, pinput, ptmp, poutput):
        input_img = pinput.convert("RGB")
        tmp_img = ptmp.convert("RGB")    
        output_img = poutput.convert("RGB")

        if input_img.size != tmp_img.size or input_img.size != output_img.size: raise Exception("All images must have the same size.")

        diff_embed = PIL.ImageChops.difference(input_img, tmp_img)
        diff_embed_np = np.array(diff_embed).astype(np.int16)  # pour éviter les overflows
        max_diff = np.max(diff_embed_np)
        if max_diff == 0:
            diff_embed_visible = PIL.Image.fromarray(np.zeros_like(diff_embed_np, dtype=np.uint8))
        else:
            scaled = (diff_embed_np * (255.0 / max_diff)).clip(0, 255).astype(np.uint8)
            diff_embed_visible = PIL.Image.fromarray(scaled)

        diff_final = PIL.ImageChops.difference(input_img, output_img)
        diff_final_np = np.array(diff_final).astype(np.int16)
        max_diff_final = np.max(diff_final_np)
        if max_diff_final == 0:
            diff_final_visible = PIL.Image.fromarray(np.zeros_like(diff_final_np, dtype=np.uint8))
        else:
            scaled_final = (diff_final_np * (255.0 / max_diff_final)).clip(0, 255).astype(np.uint8)
            diff_final_visible = PIL.Image.fromarray(scaled_final)

        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        axs[0, 0].imshow(input_img)
        axs[0, 0].set_title("Original image")
        axs[0, 0].axis("off")
        axs[0, 1].imshow(output_img)
        axs[0, 1].set_title("Steganographed image")
        axs[0, 1].axis("off")
        axs[1, 0].imshow(diff_embed_visible)
        axs[1, 0].set_title("Difference (Secret only)")
        axs[1, 0].axis("off")
        axs[1, 1].imshow(diff_final_visible)
        axs[1, 1].set_title("Difference (Secret + Noise)")
        axs[1, 1].axis("off")
        plt.tight_layout()
        plt.show()
