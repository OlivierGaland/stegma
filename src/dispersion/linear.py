import sympy
from og_log import LOG

from src.tools import get_int_from_hash
from src.dispersion.base import Dispersion
from src.kwargs import validate_kwargs

class LinearDispersion(Dispersion):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.start_offset = get_int_from_hash(self.entropy,self.limit)
        self._set_start_offset_from_entropy(0,self.limit)
        i = get_int_from_hash(self.entropy,self.limit-1)+1
        while sympy.gcd(i,self.limit) != 1: i = (i + 1) % self.limit    # better get increment with gcd(i,limit) == 1 to maximize covered space
        self.increment = i
        LOG.info("Created : "+str(self))

    def inc_offset(self,offset):
        return (offset + self.increment) % self.limit

    def __str__(self):
        return f"{self.__class__.__name__} : increment={self.increment}, limit={self.limit}, start_offset={self.start_offset}"








