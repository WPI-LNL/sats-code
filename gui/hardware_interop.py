import onewire_interface
import wiegand_interface

class Hardware_Interop:
    def __init__(self, callback_UpdateSlot: callable, callback_HardwareStateChange: callable, callback_IDScan: callable):
        onewire_interface.registerCallback_UpdateSlot(callback_UpdateSlot)
        onewire_interface.registerCallback_HardwareStateChange(callback_HardwareStateChange)
        wiegand_interface.registerCallback(callback_IDScan)

    def setStatusColor(self, position: int, color: tuple[int]):
        onewire_interface.setStatusColor(position, color)
    
    def setStatusColors(self, colors: list[tuple[int]]):
        onewire_interface.setStatusColors(colors)

    def isDoorOpen(self) -> bool:
        pass
