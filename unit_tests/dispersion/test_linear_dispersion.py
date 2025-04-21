import unittest
from src.dispersion.linear import LinearDispersion  # ajuste selon ton arborescence
import sympy,hashlib,random
from faker import Faker

class TestLinearDispersion(unittest.TestCase):

    def setUp(self):
        self.fake = Faker()

    def test_dispersion_full_cycle(self):

        for _ in range(100):
            limit =  random.randint(256,4096)  
            entropy =  hashlib.sha256(self.fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True).encode("utf-8")).hexdigest()

            disp = LinearDispersion(entropy=entropy, limit=limit)
            self.assertTrue(sympy.gcd(disp.increment, disp.limit) == 1, f"Increment {disp.increment} not coprime with limit {disp.limit}")

            visited = set()
            offset = disp.start_offset
            for _ in range(limit):
                self.assertNotIn(offset, visited, "Offset repeated before completing full cycle")
                visited.add(offset)
                offset = disp.inc_offset(offset)

            self.assertEqual(len(visited), limit, "Dispersion did not cover entire space")

if __name__ == '__main__':
    unittest.main()
