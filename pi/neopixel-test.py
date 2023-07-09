#!/usr/bin/python3
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D10

# The number of NeoPixels
num_pixels = 6

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)


while True:
    # Comment this line out if you have RGBW/GRBW NeoPixels
    pixels.fill((255, 0, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((255, 0, 0, 0))
    pixels.show()
    time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    pixels.fill((0, 255, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 255, 0, 0))
    pixels.show()
    time.sleep(1)

    # Comment this line out if you have RGBW/GRBW NeoPixels
    pixels.fill((0, 0, 255))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255, 0))
    pixels.show()
    time.sleep(1)
    
    # Comment this line out if you have RGBW/GRBW NeoPixels
    pixels.fill((0, 0, 0))
    # Uncomment this line if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255, 0))
    pixels.show()
    time.sleep(1)

    #rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
    import subprocess
    decoder = {"00003e09a09d": (255, 0, 0), "00003e088796": (0, 255, 0), "00003e0852fd": (250, 100, 0), "00003e08136c": (0, 0, 255), "00003e09aff6": (255, 255, 0)}
    p = subprocess.Popen(["sudo", "/home/pi/hacka-code/1wire/1wire"], stdout = subprocess.PIPE)
    while True:
        output_str = p.stdout.readline().decode('utf-8')
        #print(output_str)
        if "FOB ADDED" in output_str:
            i = int(output_str.split("#")[1].split(",")[0])
            if "2d-" in output_str:
                print(f"Inserted @ {i} : {decoder[output_str.strip().split('2d-')[1].strip()]} | {output_str.strip().split('2d-')[1].strip()}")
                pixels[i] = decoder[output_str.strip().split("2d-")[1].strip()]
                pixels.show()
        if "FOB REMOVED" in output_str:
            i = int(output_str.split("#")[1].split(",")[0])
            pixels[i] = (0, 0, 0);
            pixels.show()


