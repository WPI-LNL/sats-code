import onewire_interface

class Hardware_Interop:
    def change_callback(changes: tuple):
        pass

    def __init__(self):
        onewire_interface.registerCallback(Hardware_Interop.change_callback)
