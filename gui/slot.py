from datetime import datetime
from typing_extensions import override
import customtkinter as ctk
from db_interop import DB_Interop, AssetStatus

_UNKNOWN_ASSET_ID = ["UNK", "00003e09aff6"]

class Slot:
    def __init__(self, position: int, id: str, display_name: str, has_asset: bool):
        self.id = id
        self.position = position
        self.has_asset = has_asset
        self.label = lambda: self.display_name if self.display_name else "< UNKNOWN >" if self.has_asset else ""
        self.valid_id = lambda: (self.id not in _UNKNOWN_ASSET_ID) & (self.id is not None)
        self.status = lambda: \
            AssetStatus.OUT if not self.has_asset else \
            AssetStatus.IN if self.display_name else \
            AssetStatus.REGISTER if self.valid_id() else \
            AssetStatus.SCANNING if self.id is None else \
            AssetStatus.UNKNOWN
        self.display_name = None
    
    def setAssetDisplayName(self) -> str:
        if (self.id is None) | (self.id == _UNKNOWN_ASSET_ID): self.display_name = None
        else: 
            db_asset = DB_Interop.get_asset(self.id)
            self.display_name = db_asset["asset_display_name"] if db_asset["status_code"] == 200 else None 
        return self.display_name
    
    def update(self, has_asset: bool, id: str):
        if (id != self.id) & self.has_asset: # different ID --> last asset removed
            self.id = None
            self.display_name = None
            self.has_asset = False
            DB_Interop.update_asset(self.id, self.position, datetime.now(), AssetStatus.OUT)
        if has_asset: # new asset added
            self.id = id
            self.has_asset = True
            if self.setAssetDisplayName(): # asset ID in database
                DB_Interop.update_asset(self.id, self.position, datetime.now(), AssetStatus.IN)
            elif self.valid_id(): # asset ID not in database, need to register
                DB_Interop.create_asset(id, self.position, datetime.now(), AssetStatus.UNKNOWN)
                raise RegisterAssetException(id, self)


    def __str__(self):
        return self.display_name
    
    def __int__(self):
        return self.position
    
class SlotManager:
    def __init__(self, slots: list[Slot] = [Slot(i, None, None, False) for i in range(20)], widget_list: list[ctk.CTkButton] = []):
        self.slots: list[Slot] = slots
        self.widget_list: list[ctk.CTkButton] = widget_list

    def setWidgetList(self, widget_list: list[ctk.CTkButton]):
        self.widget_list = widget_list
    
    def getByPosition(self, position: int) -> Slot:
        return self.slots[position]
    
    def getByID(self, id: str) -> Slot:
        return next((i for i in self.slots if i.id == id), None)

    def setSlot(self, position: int, id: str, has_asset: bool = None):
        self.slots[position].update(has_asset if has_asset is not None else (True if id else False), id)
        if self.widget_list: self.widget_list[position].refresh()
        # return self.slots[position]
    
    def setSlots(self, ids: list[str]): # -> list[Slot]:
        for i in range(len(self.slots)):
            self.setSlot(i, ids[i] if i < len(ids) else None)
        # return self.slots

class RegisterAssetException(Exception):
    def __init__(self, id: str, slot: Slot):
        self.id = id
        self.slot = slot

    def __str__(self):
        return "Unknown asset ID " + self.id + " in slot " + str(self.slot.position) + "."