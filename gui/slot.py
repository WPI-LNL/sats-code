from datetime import datetime
from typing_extensions import override

from db_interop import DB_Interop, AssetStatus

class Slot:
    def __init__(self, position: int, id: str, display_name: str, has_asset: bool):
        self.id = id
        self.position = position
        self.has_asset = has_asset
        self.label = lambda: self.display_name if self.display_name else "Unknown" if self.has_asset else ""
        self.status = lambda: AssetStatus.OUT if not self.has_asset else AssetStatus.IN if self.display_name else AssetStatus.UNKNOWN
        self.status_color = lambda: (0,255,0) if self.status == AssetStatus.IN else (0,0,255) if self.status == AssetStatus.UNKNOWN else (0,0,0)
    
    def setAssetDisplayName(self) -> str:
        if not self.id: self.display_name = None
        else: self.display_name = (db_asset := DB_Interop.get_asset(self.id))["asset_display_name"] if db_asset.status_code == 200 else None 
        return self.display_name
    
    def update(self, has_asset: bool, id: str):
        if id != self.id & self.has_asset: # different ID --> last asset removed
            DB_Interop.update_asset(self.id, self.position, datetime.now(), AssetStatus.OUT)
            self.id, self.display_name = None
            self.has_asset = False
        if has_asset & id is not None: # new asset added
            self.id = id
            if self.setAssetDisplayName():
                DB_Interop.update_asset(self.id, self.position, datetime.now(), AssetStatus.IN)
            else:
                DB_Interop.create_asset(id, self.position, datetime.now(), AssetStatus.UNKNOWN)


    def __str__(self):
        return self.display_name
    
    def __int__(self):
        return self.position
    
class SlotManager:
    def __init__(self, slots: list[Slot] = [Slot(i, None, None, False) for i in range(20)]):
        self.slots: list[Slot] = slots
    
    def getByPosition(self, position: int) -> Slot:
        return self.slots[position]
    
    def getByID(self, id: str) -> Slot:
        return next((i for i in self.slots if i.id == id), None)

    def setSlot(self, position: int, id: str) -> Slot:
        self.slots[position].update(id)
        return self.slots[position]