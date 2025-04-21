import hashlib
import sys,time

class ProgressBar():

    def is_container(obj):
        try:
            iter(obj)
            return not isinstance(obj, str)
        except TypeError:
            return False

    def __init__(self, text_list, start_list, total_list, update_interval_percent=1, min_update_interval_sec=0.2, bar_length=100):
        if ProgressBar.is_container(text_list) and ProgressBar.is_container(start_list) and ProgressBar.is_container(total_list):
            if len(text_list) != len(start_list) or len(start_list) != len(total_list):
                raise Exception("text_list, start_list and total_list must have the same length")
        elif not ProgressBar.is_container(text_list) and not ProgressBar.is_container(start_list) and not ProgressBar.is_container(total_list):
            text_list = [text_list]
            start_list = [start_list]
            total_list = [total_list]
        else:
            raise Exception("text_list, start_list and total_list must have the same length")
        self.text_list = text_list
        self.start_list = start_list
        self.total_list = total_list
        self.update_interval_percent = update_interval_percent
        self.min_update_interval_sec = min_update_interval_sec
        self.bar_length = bar_length
        self.last_update_percent = [None] * len(text_list)
        self.last_update_time = [None] * len(text_list)
        self.last_written_bars = [None] * len(text_list)

    def update(self, current):
        do_update = False
        if not ProgressBar.is_container(current): current = [current]
        for i in range(len(self.text_list)):
            percent = 100 * (current[i] - self.start_list[i]) / (self.total_list[i] - self.start_list[i])
            if percent > 100 or percent < 0: raise Exception("percent must be between 0 and 100 : " + str(percent))

            percent_threshold_exceeded = (self.last_update_percent[i] is None or
                                          percent > self.last_update_percent[i] + self.update_interval_percent)
            time_threshold_exceeded = (self.last_update_time[i] is None or
                                       time.time() - self.last_update_time[i] >= self.min_update_interval_sec)

            if percent_threshold_exceeded and time_threshold_exceeded:
                do_update = True
                self.last_update_percent[i] = percent
                self.last_update_time[i] = time.time()

        if do_update: self._update(current)

    def _update(self, current_list):
        num_bars = len(self.text_list)

        if self.last_written_bars.count(None) == 0:
            for i in range(num_bars - 1):
                sys.stdout.write("\033[1A")
        sys.stdout.write("\r")

        for i in range(num_bars):
            text = self.text_list[i]
            current = current_list[i]
            total = self.total_list[i]

            percent = current / total
            completed = int(self.bar_length * percent)
            bar = '█' * completed + '-' * (self.bar_length - completed)

            line = f"{text} |{bar}| {int(percent * 100)}%"
            if self.last_written_bars[i] != line:
                self.last_written_bars[i] = line
                sys.stdout.write(f"{line}")

            if i < num_bars - 1: sys.stdout.write("\n")

        sys.stdout.flush()


    def end(self):
        self._update(self.total_list)
        print()


def encode_string(data: str) -> str:
    return ''.join(format(ord(c), '08b') for c in data)

def decode_string(data: str) -> str:
    return ''.join(chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8))

def get_hash_from_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def get_salted_hash_from_bytes(b: bytes, salt: bytes = b"") -> str:
    return hashlib.sha256(b + salt).hexdigest()

def xor_encrypt_decrypt(key: str, data: str):
    return ''.join(str(int(data[i]) ^ int(key[i % len(key)])) for i in range(len(data)))    

def get_int_from_hash(hash_hex: str, limit: int) -> int:
    # return determinist integer from hash ranged from 0 to limit-1
    if not isinstance(hash_hex, str): raise Exception("get_int_from_hash : Input must be a string.")
    if limit <= 0: raise Exception("get_int_from_hash : Limit must be greater than 0.")
    hash_hex = hash_hex.strip().lower().replace("0x", "")
    hash_int = int(hash_hex, 16)
    return hash_int % limit
