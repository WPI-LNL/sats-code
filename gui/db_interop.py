from datetime import datetime
from enum import Enum
import requests, urllib, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL") # default: http://lnl.wpi.edu/db/api/v1/sats/

USER_URL = "http://lnl.wpi.edu/db/"

class AssetStatus(Enum):
    UNKNOWN = 0,
    IN = 1,
    OUT = 2

class DB_Interop:
    def list_assets():
        response = requests.request("GET", API_URL + "assets/", headers={"Authorization": API_KEY}, data={})
        return response.json() | {"status_code": response.status_code}
    
    def get_asset(asset_id):
        response = requests.request("GET", API_URL + "assets/" + str(asset_id), headers={"Authorization": API_KEY}, data={})
        return response.json() | {"status_code": response.status_code}
    
    def create_asset(payload: dict):
        response = requests.request("POST", API_URL + "assets/", headers={"Authorization": API_KEY}, data=urllib.parse.urlencode(payload))
        return response.json() | {"status_code": response.status_code}
    
    def create_asset(self, asset_id: str, asset_position: int, asset_last_seen: datetime, asset_status: AssetStatus):
        payload = {
            "asset_id": asset_id, 
            "asset_position": asset_position,
            "asset_last_seen": asset_last_seen,
            "asset_status": asset_status}
        return self.create_asset(payload)

    def update_asset(payload: dict):
        response = requests.request("PATCH", API_URL + "assets/" + str(payload["asset_id"]), headers={"Authorization": API_KEY}, data=urllib.parse.urlencode(payload))
        return response.json() | {"status_code": response.status_code}
    
    def update_asset(self, asset_id: str, asset_position: int, asset_last_seen: datetime, asset_status: AssetStatus):
        payload = {
            "asset_id": asset_id, 
            "asset_position": asset_position,
            "asset_last_seen": asset_last_seen,
            "asset_status": asset_status}
        return self.update_asset(payload)
    
    def get_user(user_id, callback:function = None):
        pass

class DB_URL:
    def associate_badge(badge_id):
        return USER_URL # TODO: implement URL

    def create_asset(asset_id):
        return USER_URL # TODO: implement URL
