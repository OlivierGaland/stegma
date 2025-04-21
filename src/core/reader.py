
from og_log import LOG

from src.core.base import SteganoManager


class SteganoReader(SteganoManager):

    def __init__(self):
        self.media = None
        self.codec = None
        self.algo = None
        self.dispersion = None

    def decode(self):
         self.data = self.media.decode(self.algo,self.codec,self.dispersion)        

    def retrieve_data(self):
        return self.data

