import sympy
from og_log import LOG

from src.tools import get_int_from_hash

class Dispersion:

    def __init__(self,hash,limit):
        self.hash = hash
        self.limit = limit
        self.clear()

    def inc_offset(self,offset):
        self.idx += 1
        if (offset % self.limit) in self.cycled_idx: raise Exception("Cycled offset") # already cycled offset
        self.cycled_idx.append(offset % self.limit)
        return self._inc_offset(offset)

    def clear(self):
        self.idx = 0
        self.cycled_idx = []

    def __str__(self):
        return f"Dispersion(hash={self.hash}, limit={self.limit}, start_offset={self.start_offset})"

class NaiveDispersion(Dispersion):

    def __init__(self,hash,limit):
        super().__init__(hash,limit)
        self.start_offset = get_int_from_hash(self.hash,limit)

    def _inc_offset(self,offset):
        return (offset + 1) % self.limit
    
    def __str__(self):
        return super().__str__()


class LinearDispersion(Dispersion):

    def __init__(self,hash,limit):
        super().__init__(hash,limit)
        self.start_offset = get_int_from_hash(self.hash,limit)
        i = get_int_from_hash(hash,limit-1)+1
        while sympy.gcd(i,limit) != 1: i = (i + 1) % limit    # better get increment with gcd(i,limit) == 1 to maximize covered space
        self.increment = i
        LOG.info(self)

    def _inc_offset(self,offset):
        return (offset + self.increment) % self.limit
    
    def __str__(self):
        return super().__str__() + f", increment={self.increment}"

class ZpStarDispersion(Dispersion):

    def __init__(self,hash,limit):
        super().__init__(hash,limit)
        d = get_int_from_hash(hash,limit // 32)
        self.prime = sympy.prevprime(limit - d)  # limit > n > limit - d  , use p first prime < n
        self.start_offset = get_int_from_hash(self.hash,self.prime-1)+1
        g = get_int_from_hash(hash,self.prime-1)+1
        while not sympy.is_primitive_root(g, self.prime): g = (g + 1) % self.prime # get generator to cover [1,prime-1] of [0,limit-1] space
        self.generator = g
        LOG.info(self)

    def _inc_offset(self,offset):
        return (offset * self.generator) % self.prime
    
    def __str__(self):
        return super().__str__() + f", prime={self.prime}, generator={self.generator}"


