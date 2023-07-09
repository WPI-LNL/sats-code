from datetime import datetime
from enum import Enum
import requests, socket, urllib, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY", "DEFUALT_KEY")
API_URL = os.getenv("API_URL", "http://lnl.wpi.edu/db/api/v1/sats/") # default: http://lnl.wpi.edu/db/api/v1/sats/

USER_URL = "https://example.com"

class AssetStatus(Enum):
    UNKNOWN = 0,
    IN = 1,
    OUT = 2,
    REGISTER = 3,
    SCANNING = 4,

def is_online(host="8.8.8.8", port=53, timeout=3):
        """
        Source: StackOverflow#3764291
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        Open port: 53/tcp
        Service: domain (DNS/TCP)
        """
        return False
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            # print(ex)
            return False

class DB_Interop:
    def list_assets() -> dict:
        if not is_online(): return DB_Interop.list_assets__offline()
        response = requests.request("GET", API_URL + "assets/", headers={"Authorization": API_KEY}, data={})
        return {"status_code": response.status_code} if not response.ok else response.json() | {"status_code": response.status_code}
    
    def list_assets__offline() -> dict:
        return {}
    
    def get_asset(asset_id) -> dict:
        if not is_online(): return DB_Interop.get_asset__offline(asset_id)
        response = requests.request("GET", API_URL + "assets/" + str(asset_id), headers={"Authorization": API_KEY}, data={})
        return {"status_code": response.status_code} if not response.ok else response.json() | {"status_code": response.status_code}
    
    def get_asset__offline(asset_id) -> dict:
        if not "new" in asset_id.lower():
            return {"asset_id": asset_id, "asset_display_name": "Temp " + str(asset_id), "asset_position": 0, "asset_last_seen": datetime.now(), "asset_status": AssetStatus.IN, "status_code": 200}
        else:
            return {"asset_id": asset_id, "asset_display_name": None, "asset_position": 0, "asset_last_seen": datetime.now(), "asset_status": AssetStatus.REGISTER, "status_code": 200}
    
    def create_asset_dict(payload: dict) -> dict:
        if not is_online(): return DB_Interop.create_asset_dict__offline(payload)
        response = requests.request("POST", API_URL + "assets/", headers={"Authorization": API_KEY}, data=urllib.parse.urlencode(payload))
        return {"status_code": response.status_code} if not response.ok else response.json() | {"status_code": response.status_code}
    
    def create_asset_dict__offline(payload: dict) -> dict:
        return {"asset_display_name": "Temp " + str(payload["asset_id"]), "asset_position": payload["asset_position"], "asset_last_seen": payload["asset_last_seen"], "asset_status": payload["asset_status"], "status_code": 200}
    
    def create_asset(asset_id: str, asset_position: int, asset_last_seen: datetime, asset_status: AssetStatus) -> dict:
        payload = {
            "asset_id": asset_id, 
            "asset_position": asset_position,
            "asset_last_seen": asset_last_seen,
            "asset_status": asset_status}
        return DB_Interop.create_asset_dict(payload)

    def update_asset_dict(payload: dict) -> dict:
        if not is_online(): return DB_Interop.update_asset_dict__offline(payload)
        response = requests.request("PATCH", API_URL + "assets/" + str(payload["asset_id"]), headers={"Authorization": API_KEY}, data=urllib.parse.urlencode(payload))
        return {"status_code": response.status_code} if not response.ok else response.json() | {"status_code": response.status_code}
    
    def update_asset_dict__offline(payload: dict) -> dict:
        return {"asset_display_name": "Temp " + str(payload["asset_id"]), "asset_position": payload["asset_position"], "asset_last_seen": payload["asset_last_seen"], "asset_status": payload["asset_status"], "status_code": 200}
    
    def update_asset(asset_id: str, asset_position: int, asset_last_seen: datetime, asset_status: AssetStatus) -> dict:
        payload = {
            "asset_id": asset_id, 
            "asset_position": asset_position,
            "asset_last_seen": asset_last_seen,
            "asset_status": asset_status}
        return DB_Interop.update_asset_dict(payload)
    
    def get_user(user_id, callback: callable = None):
        if not is_online(): return DB_Interop.get_user__offline(user_id)
        pass

    def get_user__offline(user_id, callback: callable = None):
        pass

class DB_URL:
    def associate_badge(badge_id):
        return USER_URL + '/associate_badge/' + urllib.parse.quote(badge_id) + '/' # TODO: implement URL

    def create_asset(asset_id):
        return USER_URL + '/create_asset/' + urllib.parse.quote(asset_id) + '/' # TODO: implement URL
