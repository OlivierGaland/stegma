from collections import Counter
from og_log import LOG

from src.algo.base import Algo
from src.kwargs import validate_kwargs
from src.media.image import Image

class Lsb(Algo):

    def _validate_pattern(self):
        count = Counter(self.pattern)
        is_valid = (
            all(count[char] <= 1 for char in 'RGBA') and
            sum(count[char] for char in 'RGBA') <= 4 and
            sum(count.values()) == len(self.pattern)
        )
        if not is_valid:
            raise ValueError("Invalid RGBA pattern")

    def _get_encoding_pattern(self):
        if self.media == Image:
            return self.media.Generate_bit_pattern(self.coding_bits, self.pattern)
        raise Exception("Invalid media")

    @validate_kwargs({ 'mandatory': ['coding_bits', 'pattern'] })
    def __init__(self, media, **kwargs):
        self.media = media
        self.coding_bits = kwargs.pop('coding_bits')
        self.pattern = kwargs.pop('pattern')
        self._validate_pattern()
        self.encoding_pattern = self._get_encoding_pattern()
        LOG.info("Encoding pattern : "+str(self.encoding_pattern))


    def get_coding_bit_count(self,media):
        r = media.get_bit_count * (1 - self.encoding_pattern.count(0) / len(self.encoding_pattern))
        if r.is_integer(): return int(r)
        raise Exception("Invalid coding bit count")






