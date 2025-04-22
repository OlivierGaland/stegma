class SteganoManager:

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


