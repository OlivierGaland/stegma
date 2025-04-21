import hashlib
from og_log import LOG

from src.kwargs import validate_kwargs

# @validate_kwargs_ext({
#     'mandatory': ['param1', 'param2'],
#     'optional': [
#         'param3', 
#         {'name': 'param4', 'default': 'default_value'}
#     ],
#     'exclusive': [
#         [{'name': 'param5', 'mandatory': True}, {'name': 'param6', 'mandatory': True}],
#         [{'name': 'param7', 'mandatory': False, 'default': 'default_param7'}, {'name': 'param8', 'mandatory': True}]
#     ]
# })

class Codec:

    @property
    def encoded(self):
        return self.output

    @property
    def decoded(self):
        return self.input

    @validate_kwargs({
        'mandatory': ['password'],
        'optional': ['encode'],
    })
    def __init__(self,**kwargs):
        self.password = kwargs.pop('password')
        self.key = ''.join(format(byte, '08b') for byte in hashlib.sha256(self.password.encode("utf-8")).digest())
        if 'encode' in kwargs:
            self.input = kwargs.pop('encode') if 'encode' in kwargs else None
            self._encode() 
        else:
            self.input = None
            self.output = None
        LOG.info(f"{self.__class__.__name__} : {str(self)}")

    def _encode(self):
        raise Exception("Not implemented")

    def _decode(self,data):
        raise Exception("Not implemented")

    @staticmethod
    def Xor_encrypt_decrypt(key: str, data: str):
        return ''.join(str(int(data[i]) ^ int(key[i % len(key)])) for i in range(len(data)))    

    def decode(self,data):
        self._decode(data)

    def __str__(self):
        return f"Codec(password={self.password}, input={self.input}, output={self.output})"


    def extract_size(self,data=None):
        raise Exception("Not implemented")

