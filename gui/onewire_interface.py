#!/usr/bin/python3
import subprocess
import threading

class OneWireInterfaceThread:
    def __init__(self, callback: callable):
        self._updateSlot_callback = callback
        self._UIDs_callback = lambda x: None
        self._presence_callback = lambda x: None
        self.process = subprocess.Popen(["sudo", "/home/pi/hacka-code/1wire/1wire"], stdout = subprocess.PIPE)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            output_str = self.process.stdout.readline().decode('utf-8')
            #print(output_str)
            if "FOB ADDED" in output_str:
                # Message format: printf("FOB ADDED: SLOT #%d, UID %s\n", slot, uid);
                # Alternatively: printf("FOB ADDED: SLOT #%d, NO UID\n", slot);
                slot_id = int(output_str.split("#")[1].split(",")[0])
                uid = output_str.split("#")[1].split(",")[1].replace("NO UID", "UNK").replace("UID ","").strip()
                self._updateSlot_callback(slot_id, uid, True)

            if "FOB REMOVED" in output_str:
                # Message format: printf("FOB REMOVED: SLOT #%d\n", slot);
                slot_id = int(output_str.split("#")[1].split(",")[0])
                self._updateSlot_callback(slot_id, "", False)

            if "Presence:" in output_str:
                # Message format: "Presence: <True/False>, <>, ... <>, <>\n"
                uids = [bool(i) for i in output_str.split(":")[1].strip().split(", ")]
                self._presence_callback(uids)

    def request(self, msg: str):
        self.process.stdin.write(msg+"\n")
import os
if os.uname()[1] == 'raspberrypi':
    class OneWireInterface:

        def __init__(self, _callback: callable):
            self._thread = OneWireInterfaceThread(_callback)

        # sets a function to be used as the callback (i.e. the driver will call it when a device is changed)
        # Callback is called with int and str: int is the slot number, str is the UID of the device
        def registerCallback_UpdateSlot(self, callback):
            self._thread._callback = callback

        # Callback is called with single string argument: "NOMINAL", "REINSERT_LAST", or "REINSERT_ALL"
        def registerCallback_HardwareStateChange(callback):
            pass

        # return 20-element list of UIDs for present fobs, or 0 for empty slots
        def getUIDs(self, callback: callable = None):

            # TODO replace with read from /sys/bus/w1/devices/w1_bus_master1/w1_master_slaves
            return
            # return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00003e09a09d2d, 0, 0, 0, 0, 0, 0, 0, 0];

        # return 20-elemnt list of ints, 1 if a fob is present in that slot, 0 otherwise
        def getPresence(self, callback: callable = None):
            if callback: self._presence_callback = callback
            self._thread.request("getPresence")
            #return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0];

        # return a variable-length list of UIDs. These are the UIDs the devie regularly scans for
        # when a jack is inserted or removed; NOT just the ones currently present
        def getKnownUIDs():
            pass #[0x00003e09a09d2d]

        # add a UID to the list that the device regularly scans for
        def registerUID(uid):
            pass

        # trigger the device to run a full search of the address space.
        # returns a variable length list of all UIDs found on the bus
        def scanBus():
            pass # return [0x00003e09a09d2d]
else:
    class OneWireInterface:
        def __init__(self, _callback: callable):
            pass
        def registerCallback_UpdateSlot(self, callback):
            pass
        def registerCallback_HardwareStateChange(callback):
            pass
        def getUIDs(self, callback: callable = None):
            pass
        def getPresence(self, callback: callable = None):
            pass
        def getKnownUIDs():
            pass
        def registerUID(uid):
            pass
        def scanBus():
            pass
        