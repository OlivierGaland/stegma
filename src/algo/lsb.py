from og_log import LOG

from src.algo.base import Algo
from src.kwargs import validate_kwargs

class Lsb(Algo):

    @validate_kwargs({ 'mandatory': ['coding_bits', 'pattern'] })
    def __init__(self, media, **kwargs):
        self.media = media
        self.coding_bits = kwargs.pop('coding_bits')
        self.pattern = kwargs.pop('pattern')
        self.media.validate_pattern(self.pattern)
        self.encoding_pattern = self.media.generate_lsb_encoding_pattern(self.coding_bits, self.pattern)
        LOG.info("Encoding pattern : "+str(self.encoding_pattern))

    def get_coding_bit_count(self):
        r = self.media.get_bit_count * (1 - self.encoding_pattern.count(0) / len(self.encoding_pattern))
        if r.is_integer(): return int(r)
        raise Exception("Invalid coding bit count")






