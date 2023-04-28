#!/usr/bin/python3


# sets a function to be used as the callback (i.e. the driver will call it when a device is changed)
# callback should have a list of tuples as the argument; it will be invoked with a list of changes
# since the last invocation in the form of [(UID, 0), (UID, 1)...] where a 1 represents an inserted fob
# and a 0 represents a removed fob
def registerCallback(callback):
    pass

# return 20-element list of UIDs for present fobs, or 0 for empty slots
def getUIDs():
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00003e09a09d2d, 0, 0, 0, 0, 0, 0, 0, 0];

# return 20-elemnt list of ints, 1 if a fob is present in that slot, 0 otherwise
def getPresence():
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0];

# return a variable-length list of UIDs. These are the UIDs the devie regularly scans for
# when a jack is inserted or removed; NOT just the ones currently present
def getKnownUIDs():
    return [0x00003e09a09d2d]

# add a UID to the list that the device regularly scans for
def registerUID(uid):
    pass

# trigger the device to run a full search of the address space.
# returns a variable length list of all UIDs found on the bus
def scanBus():
    return [0x00003e09a09d2d]
