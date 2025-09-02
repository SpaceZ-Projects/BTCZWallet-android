
from toga import App, Box, Button, ImageView
from ..framework import CopyText
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER
from toga.colors import rgb, BLACK, YELLOW, GRAY, WHITE, GREENYELLOW

from .storage import WalletStorage


class Receive(Box):
    def __init__(self, app:App, utils):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment=CENTER
            )
        )

        self.app = app
        self.utils = utils

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

        width = self.utils.screen_size()
        qr_width = width - 120

        self.address = None

        self.transparent_button = Button(
            text="Transparent",
            enabled=False,
            style=Pack(
                color = BLACK,
                background_color=YELLOW,
                font_size=button_size,
                flex=1,
                padding = 3
            ),
            on_press=self.show_transparent_qr
        )

        self.shielded_button = Button(
            text="Shielded",
            style=Pack(
                color =WHITE,
                background_color=GRAY,
                font_size=button_size,
                flex=1,
                padding = 3
            ),
            on_press=self.show_shielded_qr
        )    

        self.buttons_box = Box(
            style=Pack(
                direction=ROW,
                background_color = rgb(40,43,48),
                padding = (0,0,20,0)
            )
        )

        self.qr_view = ImageView(
            style=Pack(
                background_color=rgb(30,33,36),
                width = qr_width,
                padding = (0,0,40,0)
            )
        )

        self.copy_button = Button(
            text="Copy",
            style=Pack(
                color=BLACK,
                background_color=GREENYELLOW,
                font_size=button_size,
                width=qr_width
            ),
            on_press=self.copy_address
        )

        self.qr_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex=1
            )
        )

        self.add(
            self.buttons_box,
            self.qr_box
        )
        self.buttons_box.add(
            self.transparent_button,
            self.shielded_button
        )
        self.qr_box.add(
            self.qr_view,
            self.copy_button
        )

        self.show_qr("transparent")


    def show_qr(self, address_type):
        wallet = self.wallet_storage.get_addresses(address_type)
        if wallet:
            self.address = wallet[0]
            qr_image = self.utils.qr_generate(self.address)
            if qr_image:
                self.qr_view.image = qr_image


    async def show_transparent_qr(self, button):
        self.transparent_button.enabled = False
        self.transparent_button.style.color = BLACK
        self.transparent_button.style.background_color = YELLOW
        self.shielded_button.style.color = WHITE
        self.shielded_button.style.background_color = GRAY
        self.shielded_button.enabled = True
        self.show_qr("transparent")

    async def show_shielded_qr(self, button):
        self.shielded_button.enabled = False
        self.shielded_button.style.color = BLACK
        self.shielded_button.style.background_color = rgb(114,137,218)
        self.transparent_button.style.color = WHITE
        self.transparent_button.style.background_color = GRAY
        self.transparent_button.enabled = True
        self.show_qr("shielded")

    async def copy_address(self, button):
        CopyText(self.address)