from statemachine import StateMachine, State
from hardware_interop import Hardware_Interop
from db_interop import DB_Interop
from asset import Asset, AssetManager
from gui import *

class Main(StateMachine):
    def __init__(self):
        self.connection = None
        super().__init__()

    door_closed = State('Door Closed', initial=True) # Door closed, idle
    door_forced_open = State('Door Forced Open') # Door forced open
    loading_user = State('Loading User') # Loading user from API
    user_not_found = State('User Not Found') # User not found in API
    register_user = State('User Registration') # User not found in API, TODO: Add QR code URL
    user_rescan = State('User Rescan') # User invalid, rescan
    user_no_permission = State('User No Permission') # User does not have permission to open

    door_open = State('Door Open') # Door open, waiting for interaction
    asset_removed = State('Asset Removed') # Asset removed, waiting for interaction
    known_asset_added = State('Known Asset Added') # Know asset added, waiting for interaction
    unknown_asset_added = State('Unknown Asset Added') # Unknown asset added, waiting for interaction
    register_unknown_asset = State('Register New Asset') # Register new asset, waiting for interaction, TODO: Add QR code URL

    close_door = door_open.to(door_closed)
    force_open = door_closed.to(door_forced_open)
    id_scan = door_closed.to(loading_user)
    user_lookup_fail = loading_user.to(user_not_found)
    user_registration = user_not_found.to(register_user)
    user_id_invalid = loading_user.to(user_rescan)
    user_permission_invalid = loading_user.to(user_no_permission)
    user_lookup_success = loading_user.to(door_open)

    remove_asset = door_open.to(asset_removed)
    add_known_asset = door_open.to(known_asset_added)
    add_unknown_asset = door_open.to(unknown_asset_added)
    asset_registration = unknown_asset_added.to(register_unknown_asset)

    test_asset_list = [Asset(None, "Asset " + str(i), i, None) for i in range(20)]

    windows = {
            door_closed.name: MessageWindow(bottom_text="Scan WPI ID to begin"),
            door_forced_open.name: MessageWindow(center_text="Close door\nto proceed", bottom_text="Door Forced"),
            loading_user.name: LoadingWindow(),
            user_not_found.name: MessageWindow(center_text="User Not Found.", bottom_text="Tap anywhere to register WPI ID"),
            register_user.name: QRWindow(bottom_text="Scan QR Code to register WPI ID"),
            user_rescan.name: MessageWindow(center_text="Please rescan WPI ID", bottom_text="Unable to read WPI ID"),
            user_no_permission.name: MessageWindow(center_text="Unauthorized\nContact Webmaster for access", bottom_text="User does not have permission to open door"),
            door_open.name: AssetWindow(test_asset_list, presence_list = [1 for i in range(20)]),
            asset_removed.name: MessageWindow(center_text="Asset Removed"),
            known_asset_added.name: MessageWindow(center_text="Asset Added"),
            unknown_asset_added.name: MessageWindow(center_text="Unknown Asset Added", bottom_text="Tap anywhere to register new asset"),
            register_unknown_asset.name: QRWindow(bottom_text="Scan QR Code to register asset")
        }

    def setConnection(self, connection):
        self.connection = connection
    
    def currentWindow(self) -> MainWindow:
        return self.windows[self.current_state.name]

    def on_exit_state(self, event, state):
        self.currentWindow().hide()
    
    def on_enter_state(self, event, state):
        if self.connection: self.currentWindow().update_online(self.connection.current_state_value)
        self.currentWindow().show()

class Connection(StateMachine):
    online = State('Online', value=True)
    offline = State('Offline', value=False, initial=True)

    go_online = offline.to(online)
    go_offline = online.to(offline)

    def on_exit_state(self, event, state):
        main.currentWindow().update_online(self.current_state_value)
    
    def on_enter_state(self, event, state):
        main.currentWindow().update_online(self.current_state_value)

if __name__ == "__main__":
    main = Main()
    connection = Connection()
    main.setConnection(connection)
    db_interop = DB_Interop()
    hardware_interop = Hardware_Interop()

    

    main.windows[main.door_closed.name].bind("<Return>", lambda event: main.id_scan())
    main.windows[main.loading_user.name].bind("<Return>", lambda event: main.user_lookup_success())
    main.windows[main.door_open.name].bind("<Return>", lambda event: main.windows[main.door_open.name].update([0,0,0,0]+ [Asset(None, "Asset " + str(i), i, None) for i in range(4,16)] + [0,0,0,0], [1 for i in range(16)]+[0,0,0,0]))
    main.currentWindow().mainloop()