from src.kwargs import validate_kwargs
from src.dispersion.base import Dispersion

from og_log import LOG

class NaiveDispersion(Dispersion):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._set_start_offset_from_entropy(0,self.limit)
        LOG.info("Created : "+str(self))

    def inc_offset(self,offset):
        return (offset + 1) % self.limit

    def __str__(self):
        return f"{self.__class__.__name__} : limit={self.limit}, start_offset={self.start_offset}"

    
