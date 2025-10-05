
import asyncio
import json

from toga import App, MainWindow, Box, Label, Button, TextInput, ImageView, ScrollContainer
from ..framework import ClickListener, ToastMessage
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, WHITE, BLACK, GREENYELLOW, GRAY

from .menu import Menu
from .storage import DeviceStorage, WalletStorage


class ServerSetup(ScrollContainer):
    def __init__(self, app:App, main:MainWindow, qr_scanner, script_path, utils, units):
        super().__init__()

        self.style= Pack(
            flex = 1
        )

        self.app = app
        self.main = main
        self.qr_scanner = qr_scanner
        self.script_path = script_path
        self.utils = utils
        self.units = units

        self.device_storage = DeviceStorage(self.app)
        self.wallet_storage = WalletStorage(self.app)

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            button_size = 18
            input_size = 18
            icon_width = 37
        elif 800 < x <= 1200:
            text_size = 12
            button_size = 15
            input_size = 15
            icon_width = 37
        elif 480 < x <= 800:
            text_size = 10
            button_size = 12
            input_size = 12
            icon_width = 33
        else:
            text_size = 18
            button_size = 20
            input_size = 20
            icon_width = 40

        self.main_box = Box(
            style= Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment=CENTER
            )
        )

        self.hostname_label = Label(
            text="Hostname :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                padding = (20,0,0,20)
            )
        )

        self.hostname_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48)
            )
        )

        self.hostname_input = TextInput(
            placeholder="Enter the hostname",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_change=self.update_confirm_button
        )

        self.scan_hostname = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(66,69,73),
                width=icon_width,
                padding = (7,10,0,0)
            )
        )
        self.scan_hostname._impl.native.setClickable(True)
        self.scan_hostname._impl.native.setOnClickListener(ClickListener(self.scan_qr_hostname))

        self.hostname_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 80,
                alignment=CENTER,
                padding = (0,20,20,20)
            )
        )

        self.auth_label = Label(
            text="Authorization :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                padding = (20,0,0,20)
            )
        )

        self.auth_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48)
            )
        )

        self.auth_input = TextInput(
            placeholder="Enter the authorization",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_change=self.update_confirm_button
        )

        self.scan_auth = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(66,69,73),
                width=icon_width,
                padding = (7,10,0,0)
            )
        )
        self.scan_auth._impl.native.setClickable(True)
        self.scan_auth._impl.native.setOnClickListener(ClickListener(self.scan_qr_auth))

        self.auth_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 80,
                alignment=CENTER,
                padding = (0,20,0,20)
            )
        )

        self.secret_label = Label(
            text="Secret Key :",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                padding = (20,0,0,20)
            )
        )

        self.secret_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                padding=(15,0,0,0)
            )
        )

        self.secret_input = TextInput(
            placeholder="Enter the secret key",
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_change=self.update_confirm_button
        )

        self.scan_secret = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(66,69,73),
                width=icon_width,
                padding = (7,10,0,0)
            )
        )
        self.scan_secret._impl.native.setClickable(True)
        self.scan_secret._impl.native.setOnClickListener(ClickListener(self.scan_qr_secret))

        self.secret_input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 80,
                alignment=CENTER,
                padding = (0,20,0,20)
            )
        )

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                color = BLACK,
                background_color=GRAY,
                font_size=button_size,
                padding=(20,20,20,20)
            ),
            enabled=False,
            on_press=self.save_auth
        )

        self.content = self.main_box

        self.main_box.add(
            self.hostname_box,
            self.auth_box,
            self.secret_box,
            self.confirm_button
        )
        self.hostname_box.add(
            self.hostname_label,
            self.hostname_input_box
        )
        self.hostname_input_box.add(
            self.hostname_input,
            self.scan_hostname
        )
        self.auth_box.add(
            self.auth_label,
            self.auth_input_box
        )
        self.auth_input_box.add(
            self.auth_input,
            self.scan_auth
        )
        self.secret_box.add(
            self.secret_label,
            self.secret_input_box
        )
        self.secret_input_box.add(
            self.secret_input,
            self.scan_secret
        )


    async def scan_qr_hostname(self, view):
        asyncio.ensure_future(self.handle_scan("hostname"))

    async def scan_qr_auth(self, view):
        asyncio.ensure_future(self.handle_scan("auth"))
    
    async def scan_qr_secret(self, view):
        asyncio.ensure_future(self.handle_scan("secret"))

    
    async def handle_scan(self, option):
        result = await self.qr_scanner.start_scan(15)
        if result == "__TIMEOUT__":
            ToastMessage("The scanner was timeout")
        elif result:
            if option == "hostname":
                self.hostname_input.value = result
            elif option == "auth":
                self.auth_input.value = result
            elif option == "secret":
                self.secret_input.value = result
        else:
            ToastMessage("No result")


    def update_confirm_button(self, input):
        hostname = self.hostname_input.value
        auth = self.auth_input.value
        secret = self.secret_input.value
        if hostname and auth and secret:
            self.confirm_button.style.background_color = GREENYELLOW
            if not self.confirm_button.enabled:
                self.confirm_button.enabled = True
        else:
            self.confirm_button.style.background_color = GRAY
            if self.confirm_button.enabled:
                self.confirm_button.enabled = False


    async def save_auth(self, button):
        self.confirm_button.style.color = WHITE
        self.confirm_button.style.background_color = GRAY
        self.confirm_button.text = "Connecting..."
        self.confirm_button.enabled = False
        hostname = self.hostname_input.value
        auth = self.auth_input.value
        secret = self.secret_input.value
        url = f'http://{hostname}/status'
        result = await self.utils.make_request(auth, secret, url)
        if not result or "error" in result:
            self.confirm_button.style.color = BLACK
            self.confirm_button.style.background_color = GREENYELLOW
            self.confirm_button.text = "Confirm"
            self.confirm_button.enabled = True
            ToastMessage("Failed to connect to the server")
            return
        decrypted = self.units.decrypt_data(secret, result["data"])
        result = json.loads(decrypted)
        version = result.get('version')
        min_version = (1, 4, 6)
        if not version:
            self.main.error_dialog(
                title="Update Required",
                message=f"Server version is too old. Please update to at least 1.4.6"
            )
            return
        try:
            version_tuple = tuple(int(x) for x in version.split("."))
        except ValueError:
            self.main.error_dialog(
                title="Update Required",
                message=f"Invalid server version format: {version}"
            )
            return

        if version_tuple < min_version:
            self.main.error_dialog(
                title="Update Required",
                message=f"Server version {version} is too old. Please update to at least 1.4.6"
            )
            return
        height = result.get('height')
        currency = result.get('currency')
        price = result.get('price')
        self.wallet_storage.insert_info(height, currency, price)
        self.device_storage.insert_auth(hostname, auth, secret)
        self.app.main_window.content = Menu(self.app, self.main, self.script_path, self.utils, self.units)