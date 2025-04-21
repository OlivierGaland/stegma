import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import random
from faker import Faker

from src.codec.decoy import Decoy
from src.codec.std import Standard

def random_bitstring(n):
    return ''.join(random.choice('01') for _ in range(n))

class TestCodec(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        self.password = self.fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)

    def run_codec_test(self, CodecClass):
        data = random_bitstring(random.randint(20, 500))
        c0 = CodecClass(password=self.password, encode=data)
        c1 = CodecClass(password=self.password)
        c1.decode(c0.encoded)
        self.assertEqual(c0.decoded, c1.decoded, f"{CodecClass.__name__} decoded mismatch")
        self.assertEqual(c0.encoded, c1.encoded, f"{CodecClass.__name__} encoded mismatch")

    def test_decoy_codec(self):
        for _ in range(1000):
            self.run_codec_test(Decoy)

    def test_standard_codec(self):
        for _ in range(1000):
            self.run_codec_test(Standard)

if __name__ == '__main__':
    unittest.main()



