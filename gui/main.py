from statemachine import StateMachine, State
from gui import MainWindow, MessageWindow, LoadingWindow, QRWindow, SlotWindow
from hardware_interop import Hardware_Interop
from db_interop import DB_Interop, DB_URL
from slot import Slot, SlotManager, RegisterAssetException
from gui import *

_DEFAULT_ALERT_DURATION = 5 # seconds

class Main(StateMachine):
    def __init__(self):
        self.connection = None
        self.slotManager.setWidgetList(self.windows[self.door_open.name].slot_widgets)
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
    def on_id_scan(self, id:str=None):
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
        if response["status_code"]: self.user_registration()
        elif response["door_access"]: self.user_lookup_success()
        elif not response["door_access"]: self.user_permission_invalid()
        else: self.user_id_invalid()

    user_registration = loading_user.to(register_user)
    user_lookup_success = loading_user.to(door_open)
    user_permission_invalid = loading_user.to(door_closed)
    def on_user_permission_invalid(self):
        self.currentWindow().showCenterAlert("Unauthorized\nContact Webmaster for access", _DEFAULT_ALERT_DURATION)
        self.currentWindow().showBottomAlert("User does not have permission to open door", _DEFAULT_ALERT_DURATION)
    
    asset_registration = door_open.to(register_unknown_asset)
    asset_registration_complete = register_unknown_asset.to(door_open)

    require_reinsert_last = (door_open.to(reinsert_last) | register_unknown_asset.to(reinsert_last) | reinsert_all.to(reinsert_last))
    
    require_reinsert_all = (door_open.to(reinsert_all) | register_unknown_asset.to(reinsert_all) | reinsert_last.to(reinsert_all))
    
    reinsert_complete = (reinsert_last.to(door_open) | reinsert_all.to(door_open))

    slotManager = SlotManager()

    windows: dict[str, MainWindow] = {
            door_closed.name: MessageWindow(bottom_text="Scan WPI ID to begin"),
            door_forced_open.name: MessageWindow(center_text="Close door\nto proceed", bottom_text="Door Forced"),
            loading_user.name: LoadingWindow(),
            register_user.name: QRWindow(bottom_text="User Not Found. Scan QR Code to register WPI ID"),
            door_open.name: SlotWindow(slotManager),
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
    
    def callback_UpdateSlot(self, position: int, id: str, has_asset: bool):
        try:
            hardware_interop.setStatusColor(position, (128,128,0) if has_asset else (0,0,128))
            self.currentWindow().after(250, lambda: hardware_interop.setStatusColor(position, (0,255,0) if has_asset else (0,0,0)))
            self.slotManager.setSlot(position, id, has_asset)
        except RegisterAssetException as ex:
            self.windows[self.register_unknown_asset.name].update_qrcode(DB_URL.create_asset(ex.id))
            self.windows[self.register_unknown_asset.name].update_bottom_text("Scan to register asset in slot " + str(ex.slot.position) + ' with ID "' + ex.id + '". Tap to continue.')
            self.asset_registration()

class Connection(StateMachine):
    online = State('Online', value=True)
    offline = State('Offline', value=False, initial=True)

    go_online = offline.to(online)
    go_offline = online.to(offline)
    
    def on_enter_state(self, event, state):
        main.currentWindow().update_online(self.current_state_value)
    
    def update(self):
        if Connection.is_online(): self.go_online()
        else: self.go_offline()

    def is_online() -> bool:
        DB_Interop.is_online()

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
    main.setConnection(connection)
    hardware_interop = Hardware_Interop(main.callback_UpdateSlot, main.callback_HardwareStateChange, main.on_id_scan)

    slot_events = [
        lambda: main.callback_UpdateSlot(0, None, True),
        lambda: main.callback_UpdateSlot(0, "ID1", True),
        lambda: main.callback_UpdateSlot(2, None, True),
        lambda: main.callback_UpdateSlot(2, "ID2", True),
        lambda: main.callback_UpdateSlot(1, None, True),
        lambda: main.callback_UpdateSlot(1, "UNK", True),
        lambda: main.callback_UpdateSlot(1, None, False),
        lambda: main.callback_UpdateSlot(0, None, False),
        lambda: main.callback_UpdateSlot(0, None, True),
        lambda: main.callback_UpdateSlot(0, "newID", True),
        lambda: main.callback_UpdateSlot(0, None, False),
        lambda: main.callback_UpdateSlot(0, None, True),
        lambda: main.callback_UpdateSlot(0, "Thumbdrive 1", True),
    ]
    slot_event_counter = 0

    def slot_event(e):
        global slot_event_counter
        slot_events[slot_event_counter]()
        slot_event_counter = (slot_event_counter + 1) % len(slot_events)

    main.windows[main.door_closed.name].bind("<Return>", lambda event: main.on_id_scan("sample"))
    main.windows[main.loading_user.name].bind("<Return>", lambda event: main.user_lookup_success())
    main.windows[main.door_open.name].bind("<Up>", slot_event)
    #main.windows[main.door_open.name].bind("<Return>", lambda event: main.windows[main.door_open.name].update([0,0,0,0]+ [Asset(None, "Asset " + str(i), i, None) for i in range(4,16)] + [0,0,0,0], [1 for i in range(16)]+[0,0,0,0]))
    main.windows[main.register_unknown_asset.name].bind("<Return>", lambda event: main.asset_registration_complete())
    main.currentWindow().mainloop()