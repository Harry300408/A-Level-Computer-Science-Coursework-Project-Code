from perlin_numpy import (
    generate_perlin_noise_2d, generate_fractal_noise_2d
)
import matplotlib.pyplot as plt
import pygame, os, sys, numpy as np, random

def generate_world_and_heights(seed=None, size=None, resolution=None, octaves=None, persistence=None, lacunarity=None):
     while True:
        try:
            if seed is None:
                seed = random.randint(0, 999999)

            if size is None:
                size = (256, 256)

            if resolution is None:
                resolution = (2, 2)

            if octaves is None:
                octaves = random.randrange(1, 10, 2)

            if persistence is None:
                persistence = random.uniform(0, 1)

            if lacunarity is None:
                lacunarity = random.randint(1, 4)

            np.random.seed(seed)
            height_map = generate_fractal_noise_2d(size, resolution, octaves, persistence, lacunarity)
            break

        except:
            print("Error generating height map")
            seed = random.randint(0, 999999)
            size = (256, 256)
            resolution = (2, 2)
            octaves = random.randrange(1, 10, 2)
            persistence = random.uniform(0, 1)
            lacunarity = random.randint(1, 4)
            pass   

     
     return [height_map, seed, size, resolution, octaves, persistence, lacunarity]

generate_world_and_heights()






        