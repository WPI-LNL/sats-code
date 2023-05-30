from datetime import datetime
from typing_extensions import override

from db_interop import DB_Interop, AssetStatus

class Asset:
    def __init__(self, id: str, display_name: str, position: int, last_seen: datetime):
        self.id = id
        self.position = position
        self.last_seen_datetime = last_seen if last_seen else datetime.now()
        self.status = lambda: AssetStatus.IN if self.position else AssetStatus.OUT if self.display_name else AssetStatus.UNKNOWN
        self.last_seen = lambda: datetime.now() if self.position else self.last_seen_datetime
        
        db_asset = DB_Interop.get_asset(id)
        if db_asset.status_code != 200:
            DB_Interop.create_asset(id, position, self.last_seen, self.status)
        else:
            self.display_name = db_asset["asset_display_name"]

    """def __init__(self,payload: dict):
        self.__init__(self, 
           payload["asset_id"], 
           payload["asset_display_name"], 
           payload["asset_position"], 
           payload["asset_last_seen"])"""
    
    def log(self):
        DB_Interop.update_asset(self.id, self.position, self.last_seen, self.status)
    
    def hardware_update(self, position: int):
        if self.position != position:
            if position == None:
                self.last_seen_datetime = datetime.now()
            self.position = position
            self.log()

    def db_update(self, display_name: str):
        self.display_name = display_name

    def __str__(self):
        return self.display_name
    
    def __int__(self):
        return self.position

class AssetManager:
    def __init__(self):
        self.assets = []

    def __init__(self, assets: dict):
        self.assets = []
        for asset in assets:
            self.assets.append(Asset(asset))
    
    def getAssetByPosition(self, position:int):
        next((asset for asset in self.assets if asset.position == position), None)
    
    def getAssetById(self, id:str):
        next((asset for asset in self.assets if asset.id == id), None)
    
    def getConnectedAssets(self):
        return [asset for asset in self.assets if asset.status == AssetStatus.IN]
    
    def getConnectedAssetList(self):
        asset_list = []
        for asset in self.getConnectedAssets():
            asset_list[asset.position] = asset
        return asset_list
    
    def hardwareUpdate_callback(self, changes: tuple):
        for change in changes:
            if asset := self.getAssetById(change[0]):
                asset.hardware_update(change[1])

    def hardwareUpdate_callback__lambda(self):
        return lambda changes: self.hardwareUpdate_callback(changes)
    
    def dbUpdate_callback(self, changes: dict):
        for change in changes:
            if asset := self.getAssetById(change["asset_id"]):
                asset.db_update(change["asset_display_name"])

    def create_asset(self, id, position = None, last_seen = datetime.now()):
        self.assets.append(Asset(id, None, position, last_seen))
        DB_Interop.create_asset(id, position, last_seen, AssetStatus.UNKNOWN)

class UnknownAsset(Asset):
    def __init__(self, position: int):
        self.position = position
        self.id = None
        self.last_seen_datetime = None
        self.status = AssetStatus.UNKNOWN
        self.last_seen = lambda: datetime.now()
        self.display_name = "UNKNOWN"

    @override
    def __str__(self):
        return self.display_name
    
    @override
    def __int__(self):
        return self.position
    
    @override
    def hardware_update(self, position: int):
        pass
    
    @override
    def log(self):
        pass
