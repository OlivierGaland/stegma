# import hashlib
# from og_log import LOG

# from src.tools import get_int_from_hash
# from src.dispersion.base import Dispersion

# class ChainedHashDispersion(Dispersion):

#     def __init__(self,**kwargs):
#         super().__init__(**kwargs)
#         self._set_start_offset_from_entropy(0,self.limit)
#         self.draw_offsets = [ self.start_offset ]
#         self.current_hash = self.entropy
#         LOG.info("Created : "+str(self))

#     def inc_offset(self,offset):
#         new_hash = hashlib.sha256(self.current_hash.encode("utf-8")).hexdigest()
#         new_offset = get_int_from_hash(new_hash,self.limit)
#         while new_offset in self.draw_offsets:
#             new_hash = hashlib.sha256(new_hash.encode("utf-8")).hexdigest()
#             new_offset = get_int_from_hash(new_hash,self.limit)
#         self.draw_offsets.append(new_offset)
#         self.current_hash = new_hash
#         return new_offset

#     def __str__(self):
#         return f"{self.__class__.__name__} : entropy={self.entropy}, limit={self.limit}, start_offset={self.start_offset}"

import hashlib
from og_log import LOG

from src.tools import get_int_from_hash
from src.dispersion.base import Dispersion

class ChainedHashDispersion(Dispersion):
    COLLISION_THRESHOLD = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_start_offset_from_entropy(0, self.limit)
        self.draw_offsets = [self.start_offset]
        self.current_hash = self.entropy
        LOG.info("Created : " + str(self))

    def inc_offset(self, offset):
        new_hash = hashlib.sha256(self.current_hash.encode("utf-8")).hexdigest()
        new_offset = get_int_from_hash(new_hash, self.limit)
        collision_count = 0
        while new_offset in self.draw_offsets:
            new_hash = hashlib.sha256(new_hash.encode("utf-8")).hexdigest()
            new_offset = get_int_from_hash(new_hash, self.limit)
            collision_count += 1
            if collision_count > self.COLLISION_THRESHOLD:
                LOG.warning(f"Collision count = {collision_count}, for offset {offset}.")

        self.draw_offsets.append(new_offset)
        self.current_hash = new_hash
        return new_offset

    def __str__(self):
        return f"{self.__class__.__name__} : entropy={self.entropy}, limit={self.limit}, start_offset={self.start_offset}, collision_threshold={self.COLLISION_THRESHOLD}"
    