from src.codec.base import Codec

from src.kwargs import validate_kwargs

class Decoy(Codec):

    @validate_kwargs({
        'mandatory': ['password'],
        'exclusive': [
            [{'name': 'encode'}],
            ['size']
        ]
    })
    def __init__(self,**kwargs):
        if 'size' in kwargs: self.size = kwargs.pop('size')
        super().__init__(**kwargs)

    def _encode(self):
        self.output = Codec.Xor_encrypt_decrypt(self.key,self.input)
        #print("Encoded secret size : ",len(self.output))

    def _decode(self,data):
        self.output = data
        self.input = Codec.Xor_encrypt_decrypt(self.key,self.output)

    def extract_size(self,data=None):
        if hasattr(self,'size'): return True,self.size
        return True,None
