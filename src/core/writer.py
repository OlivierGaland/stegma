from src.core.base import SteganoManager

from og_log import LOG


class SteganoWriter(SteganoManager):

    def __init__(self):
        self.media = None
        self.codec = None
        self.algo = None
        self.dispersion = None
        self.noise = None

    def encode(self):
        self.output = self.media.encode(self.algo,self.codec,self.dispersion,self.noise)        

    def write(self,filename):
        self.output.save(filename, format="PNG")
        LOG.info(f"File saved : {filename}")

    def register_noise(self,noise,**kwargs):
        self.noise = noise(**kwargs)
        
