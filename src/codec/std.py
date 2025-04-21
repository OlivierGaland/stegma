from src.codec.decoy import Codec

class Standard(Codec):

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

    def _encode(self):
        header = Standard.Build_header(len(self.input))
        self.output = header + Codec.Xor_encrypt_decrypt(self.key,self.input)

    def _decode(self,data):
        self.output = data
        for i in range(len(self.output)):
            r,h = Standard.Scan_header(self.output[:i])
            if r:
                self.input = Codec.Xor_encrypt_decrypt(self.key,self.output[i:])
                return
        raise Exception("Invalid header")

    def extract_size(self,data=None):
        if data is not None:
            try:
                return Standard.Scan_header(data)
            except Exception as e:
                return False,None
        return False,None
