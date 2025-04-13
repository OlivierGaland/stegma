from og_log import LOG
from PIL import Image
import hashlib

from src.tools import get_salted_hash_from_bytes,xor_encrypt_decrypt
from src.tools import progress_bar,progress_bar_end


def alter_img(img, offset, bit_val):
    if bit_val not in (0, 1): raise ValueError("bit_val doit être 0 ou 1")
    width, height = img.size
    total_channels = width * height * 3

    offset %= total_channels  

    pixel_index = offset // 3
    channel_index = offset % 3  # 0 = R, 1 = G, 2 = B

    x = pixel_index % width
    y = pixel_index // width

    r, g, b, a = img.getpixel((x, y))
    channels = [r, g, b]

    channels[channel_index] = (channels[channel_index] & ~1) | (bit_val & 1)

    img.putpixel((x, y), (channels[0], channels[1], channels[2], a))

    return img


def get_val(img, offset):
    width, height = img.size
    total_channels = width * height * 3  # Nombre total de canaux R, G, B (pas A)

    offset %= total_channels

    pixel_index = offset // 3
    channel_index = offset % 3  # 0 = R, 1 = G, 2 = B

    r, g, b, _ = img.getpixel((pixel_index % width, pixel_index // width))
    channels = [r, g, b]

    return channels[channel_index] & 1



class SteganoManager:

    @staticmethod
    def Build_header(length):
        if length < 1: raise Exception(f"Invalid data length: {length}")
        nbit = (length - 1).bit_length()
        if nbit <= 8: prefix, width = '0', 8
        elif nbit <= 16: prefix, width = '10', 16
        elif nbit <= 24: prefix, width = '110', 24
        elif nbit <= 32: prefix, width = '1110', 32
        else: raise Exception("Data too large (> 4Gb)")
        return prefix + format(length - 1, f'0{width}b')

    @staticmethod
    def Scan_header(dfield: str):
        l = len(dfield)
        if l == 9 and dfield.startswith('0'): return True, int(dfield[1:], 2) + 1
        elif l == 18 and dfield.startswith('10'): return True, int(dfield[2:], 2) + 1
        elif l == 27 and dfield.startswith('110'): return True, int(dfield[3:], 2) + 1
        elif l == 36 and dfield.startswith('1110'): return True, int(dfield[4:], 2) + 1
        elif l > 36: raise Exception("Invalid header: exceeded maximum header length (36 bits)")
        return False, None


class SteganoImgManager(SteganoManager):
    MIN_BIT_RATIO = 20

    @property
    def ratio(self):
        return self.pixel_count*24/len(self.crypted_data)

    @property
    def pixel_count(self):
        x,y = self.img.size
        return x*y    

    def __init__(self, algo, password, input_file):
        self.password = password
        self.key = ''.join(format(byte, '08b') for byte in hashlib.sha256(self.password.encode()).digest())
        self.img = Image.open(input_file).convert("RGBA")
        self.img_out = None
        self.dispersion = algo(get_salted_hash_from_bytes(self.get_img_bytes_for_hash(),self.password.encode("utf-8")), self.pixel_count*3)

    def get_img_bytes_for_hash(self):
        cleaned_pixels = [ (r & 0b11111110, g & 0b11111110, b & 0b11111110, a) for r, g, b, a in self.img.getdata() ]
        cleaned_img = Image.new("RGBA", self.img.size)
        cleaned_img.putdata(cleaned_pixels)
        return cleaned_img.tobytes()

class SteganoImgReader(SteganoImgManager):

    def __init__(self, algo, password, input_file):
        super().__init__(algo, password, input_file)
        self.crypted_data , header_size = self.decode_data_lsb()
        self.data = xor_encrypt_decrypt(self.key,self.crypted_data[header_size:])


    def decode_data_lsb(self):
        offset = self.dispersion.start_offset
        data = ""
        header_found = False
        while True:
            data += str(get_val(self.img, offset))
            if not header_found:
                header_found , size = SteganoManager.Scan_header(data)
                header_size = len(data)
                progress = 0
            else:
                progress_bar("Reading : ", progress, size,100)
                progress += 1
                if self.dispersion.idx >= header_size + size - 1: break
            offset = self.dispersion.inc_offset(offset)
        if header_found: progress_bar_end("Reading : ",100)

        #LOG.info("Read data : "+str(data))
        return data , header_size
        
    def __str__(self):
        return f"DataReader(password={self.password}, data_size={len(self.data)}, pixel_count={self.pixel_count})"


class SteganoImgWriter(SteganoImgManager):
    
    def __init__(self, algo, noise, password, input_file, data):
        super().__init__(algo, password, input_file)
        self.noise = noise()
        self.data = data
        header = SteganoManager.Build_header(len(self.data))
        self.crypted_data = header + xor_encrypt_decrypt(self.key,self.data)
        if xor_encrypt_decrypt(self.key,self.crypted_data[len(header):]) != self.data: raise Exception("Data content corrupted")
        if len(self.crypted_data) - len(header) != len(self.data): raise Exception("Data len corrupted")
        if self.pixel_count*24 < SteganoImgManager.MIN_BIT_RATIO*len(self.crypted_data): raise Exception("Image too small to have secret bit ratio > "+str(SteganoImgManager.MIN_BIT_RATIO))

    def __str__(self):
        #return f"DataHidder(password={self.password}, size={len(self.data)}, data={self.data}, crypted_data={self.crypted_data})"
        return f"DataHidder(password={self.password}, data_size={len(self.data)}, pixel_count={self.pixel_count}, ratio={int(self.ratio)}, offset={self.dispersion.start_offset}, crypted_data={self.crypted_data})"

    def embed_data_lsb(self,file_out):
        #LOG.info("Embedding data : "+str(self.crypted_data))
        self.img_embed = self.img.copy()
        offset = self.dispersion.start_offset
        total = len(self.crypted_data)
        for i in range(total):
            progress_bar("Embedding : ", i, total,100)
            alter_img(self.img_embed, offset, int(self.crypted_data[i]))
            offset = self.dispersion.inc_offset(offset)
        progress_bar_end("Embedding : ",100)

        self.img_out = self.img_embed.copy()
        self.noise.add_noise(self.img_out,self.dispersion.cycled_idx)
        
        self.img_embed.save(file_out+".tmp", format="PNG")
        self.img_out.save(file_out, format="PNG")
        LOG.info(f"File saved : {file_out}")



