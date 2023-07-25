#!/usr/bin/python3

try:
    import time
    import board
    import neopixel
    import digitalio
except NotImplementedError:
    class Neopixel_Interface:
        def __init__(self):
            pass
        def fill(self, color: tuple[int]):
            pass
        def set(self, position: int, color: tuple[int]):
            pass
        def setAll(self, colors: list[tuple[int]]):
            pass
else:

    pixel_pin = board.D10
    row_select_pins = [board.D0, board.D9, board.D11, board.D5]
    row_digitalio_pins = [digitalio.DigitalInOut(pin) for pin in row_select_pins]
    for pin in row_digitalio_pins:
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False
    num_pixels = 6
    ORDER = neopixel.RGB

    class Neopixel_Interface:

        def __init__(self):
            self.pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)
            self.fill((0, 0, 0))

        def fill(self, color: tuple[int]):
            for pin in row_digitalio_pins:
                pin.value = True
                self.pixels.fill(color)
                self.pixels.show()
                pin.value = False
        
        def set(self, position: int, color: tuple[int]):
            row_select_pins[int(position/5)].value = True
            self.pixels[position % (num_pixels-1)] = color
            self.pixels.show()
            row_select_pins[int(position/5)].value = False
        
        def setAll(self, colors: list[tuple[int]]):
            for row in range(len(row_digitalio_pins)):
                row_digitalio_pins[row].value = True
                for pixel in range(num_pixels):
                    self.pixels[pixel] = colors[pixel+row*4]
                self.pixels.show()
                row_digitalio_pins[row].value = False