
import asyncio
from pathlib import Path

from toga import (
    App, MainWindow, Box, ImageView, Label, Button,
    ScrollContainer, ProgressBar
)
from .framework import (
    MainActivity, AppProxy, QRScanner, SelectFolderDialog,
    Notification, TorController
)
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW
from toga.colors import rgb, WHITE, YELLOW, BLACK, GRAY

from .resources import (
    Utils, ServerSetup, Menu, DeviceStorage, Units
)



class BitcoinZGUI(MainWindow):
    def __init__(self):
        super().__init__()

        version = self.app.version

        self.units = Units()
        self.utils = Utils(self.app, self.units)
        self.device_storage = DeviceStorage(self.app)
        self.qr_scanner = QRScanner(self.app.activity)
        self.select_folder = SelectFolderDialog(self.app.activity)
        self.script_path = Path(__file__).resolve().parent

        self.tor_window = None
        self.tbalance = None
        self.zbalance = None

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            icon_width = 37
            button_size = 18
        elif 800 < x <= 1200:
            text_size = 12
            icon_width = 37
            button_size = 15
        elif 480 < x <= 800:
            text_size = 10
            icon_width = 33
            button_size = 12
        else:
            text_size = 17
            icon_width = 40
            button_size = 20

        x = self.utils.screen_size()
        logo_width = x - 65

        self.main_scroll = ScrollContainer(
            style=Pack(
                flex=1
            )
        )

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                flex = 1,
                alignment = CENTER
            )
        )

        self.bitcoinz_logo = ImageView(
            image="images/BitcoinZ.png",
            style=Pack(
                background_color =rgb(40,43,48),
                width=logo_width,
                flex=2
            )
        )

        self.slogan_label = Label(
            text="Your Gateway to the BitcoinZ Network",
            style=Pack(
                color = GRAY,
                background_color=rgb(40,43,48),
                text_align=CENTER,
                font_size=text_size,
                font_weight=BOLD
            )
        )
        self.slogan_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(40,43,48),
                alignment=CENTER,
                flex = 1
            )
        )

        self.app_version = Label(
            text=f"v {version}",
            style=Pack(
                color = WHITE,
                background_color =rgb(40,43,48),
                flex = 1,
                text_align = CENTER,
                font_size=15,
                font_weight=BOLD,
                padding = (20,0,30,0)
            )
        )

        self.tor_icon = ImageView(
            image="images/tor.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width= icon_width,
                alignment = CENTER,
                padding = (5,0,0,15)
            )
        )

        self.tor_button = Button(
            text="Mobile Server",
            style=Pack(
                color=BLACK,
                background_color = GRAY,
                font_size=button_size,
                alignment = CENTER,
                flex = 1,
                padding= (0,15,5,5)
            ),
            enabled=False,
            on_press=self.show_tor_window
        )

        self.tor_progress = ProgressBar(
            max=100,
            value=0,
            style=Pack(
                flex = 1,
                padding = (20,0,0,10)
            )
        )

        self.tor_progress_label = Label(
            text="0%",
            style=Pack(
                color=YELLOW,
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER,
                padding = (15,15,0,15)
            )
        )

        self.tor_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
            )
        )

        self.content = self.main_scroll
        self.main_scroll.content = self.main_box

        self.show_wizard()
        


    def show_wizard(self):
        self.main_box.add(
            self.bitcoinz_logo,
            self.slogan_box,
            self.tor_box,
            self.app_version
        )
        self.slogan_box.add(
            self.slogan_label
        )
        self.tor_box.add(
            self.tor_icon,
            self.tor_progress,
            self.tor_progress_label
        )

        self.app.loop.create_task(self.verify_tor_network())


    async def verify_tor_network(self):
        while True:
            progress = self.app.controller.progress
            self.tor_progress.value = progress
            self.tor_progress_label.text = f"{progress}%"
            if self.app.controller.progress == 100:
                await self.check_device_account()
                return
            await asyncio.sleep(0.1)

    
    async def check_device_account(self):
        self.tor_box.remove(
            self.tor_progress,
            self.tor_progress_label
        )
        self.tor_box.add(self.tor_button)
        await asyncio.sleep(1)
        device_auth = self.device_storage.get_auth()
        if device_auth:
            self.app.main_window.content = Menu(
                self.app, self, self.script_path, self.utils, self.units
            )
            return
        self.tor_button.style.color = BLACK
        self.tor_button.style.background_color = YELLOW
        self.tor_button.enabled = True

        

    async def show_tor_window(self, button):
        self.main_box.clear()
        tor_window = ServerSetup(
            self.app, self, self.qr_scanner, self.script_path, self.utils, self.units
        )
        self.main_box.add(tor_window)
        self.app.window_toggle = True



class BitcoinZWallet(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.proxy = AppProxy()
        self.proxy._back_callback = self.on_back_pressed
        self.activity = MainActivity.singletonThis
        self.notify = Notification(self.activity)
        self.controller = TorController(self.activity)
        self.window_toggle = None


    def startup(self):
        MainActivity.setPythonApp(self.proxy)
        self.main_window = BitcoinZGUI()
        self.main_window.show()

    def on_running(self):
        self.controller.start_tor()


    def on_back_pressed(self):
        def on_result(widget, result):
            if result is True:
                self.controller.stop_tor()
                self.proxy.Exit()
        if self.window_toggle:
            self.main_window.main_box.clear()
            self.main_window.show_wizard()
            self.window_toggle = None
            return True
        self.main_window.question_dialog(
            title="Exit app",
            message="Are you sure you want exit the app",
            on_result=on_result
        )
        return True
        

def main():
    app = BitcoinZWallet(
        icon="images/BitcoinZ",
        formal_name = "BTCZWallet",
        app_id = "com.btcz",
        home_page = "https://getbtcz.com",
        author = "BTCZCommunity",
        version = "1.0.6"
    )
    app.main_loop()

if __name__ == "__main__":
    main()