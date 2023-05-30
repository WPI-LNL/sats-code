from statemachine import StateMachine, State
from hardware_interop import Hardware_Interop
from db_interop import DB_Interop
from slot import Slot, SlotManager
from gui import *

_UNKNOWN_ASSET_ID = "UNK"
_DEFAULT_ALERT_DURATION = 5 #seconds

class Main(StateMachine):
    def __init__(self):
        self.connection = None
        super().__init__()

    door_closed = State('Door Closed', initial=True) # Door closed, idle
    door_forced_open = State('Door Forced Open') # Door forced open
    loading_user = State('Loading User') # Loading user from API
    register_user = State('User Registration') # User not found in API, TODO: Add QR code URL

    door_open = State('Door Open') # Door open, waiting for interaction
    register_unknown_asset = State('Register New Asset') # Register new asset, waiting for interaction, TODO: Add QR code URL

    reinsert_last = State('Reinsert Last') # Reinsert last asset(s), waiting for hardware validation
    reinsert_all = State('Reinsert All') # Reinsert all asset(s), waiting for hardware validation

    close_door = (door_open.to(door_closed) | door_forced_open.to(door_closed))
    force_open = door_closed.to(door_forced_open)

    await_ID_validation = door_closed.to(loading_user)
    def on_id_scan(self, id:str):
        if id is None:
            self.user_id_invalid()
        else:
            self.await_ID_validation()
            DB_Interop.get_user(id, self.callback_UserLookup)
    
    user_id_invalid = loading_user.to(door_closed)
    def on_user_id_invalid(self):
        self.currentWindow().showCenterAlert("Unable to read WPI ID", _DEFAULT_ALERT_DURATION)
        self.currentWindow().showBottomAlert("Please rescan WPI ID", _DEFAULT_ALERT_DURATION)
    
    def callback_UserLookup(self, response: dict):
        if response.status_code == 404: self.user_registration()
        elif response.door_access: self.user_lookup_success()
        elif not response.door_access: self.user_permission_invalid()
        else: self.user_id_invalid()

    user_registration = loading_user.to(register_user)
    user_lookup_success = loading_user.to(door_open)
    user_permission_invalid = loading_user.to(door_closed)
    def on_user_permission_invalid(self):
        self.currentWindow().showCenterAlert("Unauthorized\nContact Webmaster for access", _DEFAULT_ALERT_DURATION)
        self.currentWindow().showBottomAlert("User does not have permission to open door", _DEFAULT_ALERT_DURATION)

    remove_asset = door_open.to.itself()
    def on_remove_asset(self):
        self.currentWindow().showBottomAlert("Asset Removed", _DEFAULT_ALERT_DURATION)
    add_known_asset = door_open.to.itself()
    def on_add_known_asset(self):
        self.currentWindow().showBottomAlert("Asset Identified", _DEFAULT_ALERT_DURATION)
    asset_registration = door_open.to(register_unknown_asset)

    require_reinsert_last = (door_open.to(reinsert_last) | register_unknown_asset.to(reinsert_last) | reinsert_all.to(reinsert_last))
    
    require_reinsert_all = (door_open.to(reinsert_all) | register_unknown_asset.to(reinsert_all) | reinsert_last.to(reinsert_all))
    
    reinsert_complete = (reinsert_last.to(door_open) | reinsert_all.to(door_open))

    windows = {
            door_closed.name: MessageWindow(bottom_text="Scan WPI ID to begin"),
            door_forced_open.name: MessageWindow(center_text="Close door\nto proceed", bottom_text="Door Forced"),
            loading_user.name: LoadingWindow(),
            register_user.name: QRWindow(bottom_text="User Not Found. Scan QR Code to register WPI ID"),
            door_open.name: AssetWindow(test_asset_list, presence_list = [1 for i in range(20)]),
            register_unknown_asset.name: QRWindow(bottom_text="Scan QR Code to register asset"),

            reinsert_last.name: MessageWindow(center_text="Asset Not Identified", bottom_text="Remove and reinsert last asset."),
            reinsert_all.name: MessageWindow(center_text="Assets Out of Sync", bottom_text="Remove and reinsert ALL assets."),
        }

    def setConnection(self, connection):
        self.connection = connection
    
    def currentWindow(self) -> MainWindow:
        return self.windows[self.current_state.name]
    
    def before_transition(self, event, state):
        if event == self.reinsert_complete: # todo: redirect state transition depending on hardware status
            pass

    def on_exit_state(self, event, state):
        self.currentWindow().hide()
    
    def on_enter_state(self, event, state):
        if self.connection: self.currentWindow().update_online(self.connection.current_state_value)
        self.currentWindow().show()

    def callback_HardwareStateChange(self, state: str):
        match state:
            case "NOMINAL":
                self.reinsert_complete()
            case "REINSERT_LAST":
                self.reinsert_last()
            case "REINSERT_ALL":
                self.reinsert_all()
            case default:
                print("Unknown hardware state: " + state)

class Connection(StateMachine):
    online = State('Online', value=True)
    offline = State('Offline', value=False, initial=True)

    go_online = offline.to(online)
    go_offline = online.to(offline)

    def on_exit_state(self, event, state):
        main.currentWindow().update_online(self.current_state_value)
    
    def on_enter_state(self, event, state):
        main.currentWindow().update_online(self.current_state_value)

class OneWireValidation(StateMachine):
    nominal = State('Nominal', value=0, initial=True)
    reinsert = State('Reinsert', value=1)
    global_reset = State('Global Reset', value=2)

    go_nominal = (reinsert.to(nominal) | global_reset.to(nominal))
    go_reinsert = (nominal.to(reinsert) | global_reset.to(reinsert))
    go_global_reset = (nominal.to(global_reset) | reinsert.to(global_reset))

    def on_enter_nominal(self):
        main.currentWindow().update_online(self.current_state_value)

if __name__ == "__main__":
    main = Main()
    connection = Connection()
    slotManager = SlotManager()
    main.setConnection(connection)
    hardware_interop = Hardware_Interop(slotManager.setSlot, main.callback_HardwareStateChange)

    

    main.windows[main.door_closed.name].bind("<Return>", lambda event: main.id_scan())
    main.windows[main.loading_user.name].bind("<Return>", lambda event: main.user_lookup_success())
    main.windows[main.door_open.name].bind("<Return>", lambda event: main.windows[main.door_open.name].update([0,0,0,0]+ [Asset(None, "Asset " + str(i), i, None) for i in range(4,16)] + [0,0,0,0], [1 for i in range(16)]+[0,0,0,0]))
    main.currentWindow().mainloop()