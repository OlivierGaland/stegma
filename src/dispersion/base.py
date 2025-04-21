from src.tools import get_int_from_hash
from src.kwargs import validate_kwargs

class Dispersion:

    @validate_kwargs({ 'mandatory': ['entropy', 'limit'] })
    def __init__(self,**kwargs):
        self.entropy = kwargs.pop('entropy')
        self.limit = kwargs.pop('limit')

    def _set_start_offset_from_entropy(self,first,last):
        self.start_offset = get_int_from_hash(self.entropy,last-first)+first

    def inc_offset(self,offset):
        raise Exception("Not implemented")

