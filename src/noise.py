import random

from src.img import alter_img
from src.tools import progress_bar,progress_bar_end

class NoiseGenerator:

    def add_noise(self, img, cycled_idx):
        raise Exception("Not implemented")

class NoNoiseGenerator(NoiseGenerator):

    def add_noise(self, img, cycled_idx):
        return

class RandomNoiseGenerator(NoiseGenerator):

    def add_noise(self, img, cycled_idx):
        sorted_cycled_idx = sorted(cycled_idx)
        x,y = img.size
        total = x*y*3
        old_i = -1
        for i in sorted_cycled_idx:
            progress_bar("Adding noise : ", i, total,100)
            for j in range(old_i+1,i): alter_img(img, j, random.randint(0, 1))
            old_i = i
        for j in range(old_i+1,total): alter_img(img, j, random.randint(0, 1))
        progress_bar_end("Adding noise : ", 100)


