#!/usr/bin/python3

import time
import board
import neopixel

pixel_pin = board.D10
num_pixels = 6
ORDER = neopixel.RGB

class Neopixel_Interface:

    def __init__(self):
        self.pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)
        self.fill((0, 0, 0))

    def fill(self, color: tuple[int]):
        self.pixels.fill(color)
        self.pixels.show()
    
    def set(self, position: int, color: tuple[int]):
        self.pixels[position] = color
        self.pixels.show()
    
    def setAll(self, colors: list[tuple[int]]):
        for i in range(num_pixels):
            self.pixels[i] = colors[i]
        self.pixels.show()