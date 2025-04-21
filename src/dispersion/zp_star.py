import sympy
from og_log import LOG

from src.tools import get_int_from_hash
from src.dispersion.base import Dispersion

class ZpStarDispersion(Dispersion):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        d = get_int_from_hash(self.entropy,self.limit // 32)
        self.prime = sympy.prevprime(self.limit - d)  # limit > n > limit - d  , use p first prime < n
        #self.start_offset = get_int_from_hash(self.entropy,self.prime-1)+1
        self._set_start_offset_from_entropy(1,self.prime)
        g = get_int_from_hash(self.entropy,self.prime-1)+1
        while not sympy.is_primitive_root(g, self.prime): g = (g + 1) % self.prime # get generator to cover [1,prime-1] of [0,limit-1] space
        self.generator = g
        LOG.info("Created : "+str(self))

    def inc_offset(self,offset):
        return (offset * self.generator) % self.prime

    def __str__(self):
        return f"{self.__class__.__name__} : entropy={self.entropy}, limit={self.limit}, prime={self.prime}, generator={self.generator}"

