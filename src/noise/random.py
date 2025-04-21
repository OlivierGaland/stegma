import secrets
from src.noise.base import NoiseGenerator

class RandomNoiseGenerator(NoiseGenerator):
    def get(self, val):
        return secrets.randbits(1)
    