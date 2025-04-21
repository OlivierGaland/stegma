from src.noise.base import NoiseGenerator

class NoNoiseGenerator(NoiseGenerator):
    
    def get(self, val):
        return None

