import unittest
import sympy
import hashlib
import random
from faker import Faker

from src.dispersion.zp_star import ZpStarDispersion  # ajuste l'import si besoin

class TestZpStarDispersion(unittest.TestCase):

    def setUp(self):
        self.fake = Faker()

    def test_dispersion_full_cycle(self):
        for _ in range(100):
            limit = random.randint(256, 4096)  # garde une taille raisonnable pour la vitesse
            entropy = hashlib.sha256(
                self.fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True).encode("utf-8")
            ).hexdigest()

            disp = ZpStarDispersion(entropy=entropy, limit=limit)

            # Vérifie que le générateur est bien un générateur de Z*_p
            self.assertTrue(sympy.is_primitive_root(disp.generator, disp.prime), 
                            f"{disp.generator} is not a primitive root of {disp.prime}")

            visited = set()
            offset = disp.start_offset

            # On attend un cycle sur Z*_p, donc prime-1 éléments
            for _ in range(disp.prime - 1):
                self.assertNotIn(offset, visited, f"Offset {offset} repeated before completing full cycle")
                visited.add(offset)
                offset = disp.inc_offset(offset)

            self.assertEqual(len(visited), disp.prime - 1, 
                             f"Cycle length incorrect: expected {disp.prime - 1}, got {len(visited)}")

if __name__ == '__main__':
    unittest.main()
