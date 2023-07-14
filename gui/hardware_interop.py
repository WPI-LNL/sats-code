from onewire_interface import OneWireInterface
from wiegand_interface import Wiegand_Interface
from neopixel_interface import Neopixel_Interface
class Hardware_Interop:
    def __init__(self, callback_UpdateSlot: callable, callback_HardwareStateChange: callable, callback_IDScan: callable):
        self.onewire_interface = OneWireInterface(callback_UpdateSlot)
        self.wiegand_interface = Wiegand_Interface(callback_IDScan)
        self.neopixel_interface = Neopixel_Interface()

    def setStatusColor(self, position: int, color: tuple[int]):
        self.neopixel_interface.set(position, color)
    
    def setAllStatusColors(self, colors: list[tuple[int]]):
        self.neopixel_interface.setStatusColors(colors)

    def setCardReaderLED(self, state: bool):
        self.wiegand_interface.setLED(state)

    def isDoorOpen(self) -> bool:
        pass