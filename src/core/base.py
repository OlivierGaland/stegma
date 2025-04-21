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


    def register_codec(self,codec,**kwargs):
        self.codec = codec(**kwargs)

    def register_media(self,media,**kwargs):
        self.media = media(**kwargs)

    def register_algo(self,algo,**kwargs):
        if self.media is None: raise Exception("Media class must be registered before registering an algorithm.")
        self.algo = algo(type(self.media),**kwargs)

    def register_dispersion(self,dispersion,**kwargs):
        if self.media is None: raise Exception("Media class must be registered before registering a dispersion.")
        if self.codec is None: raise Exception("Codec must be registered before registering a dispersion.")
        kwargs['limit'] =  self.algo.get_coding_bit_count(self.media)
        kwargs['entropy'] = self.media.entropy(self.codec.password)
        self.dispersion = dispersion(**kwargs)


