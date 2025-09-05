
import os

from toga import App, MainWindow, Box, Button, ImageView, MultilineTextInput
from ..framework import (
    CopyText, ToastMessage, Uri, DocumentFile,
    FileInputStream
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, BLACK, YELLOW, GRAY, WHITE, GREENYELLOW

from .storage import WalletStorage


class Receive(Box):
    def __init__(self, app:App, main:MainWindow, utils):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment=CENTER
            )
        )

        self.app = app
        self.main = main
        self.utils = utils

        self.wallet_storage = WalletStorage(self.app)

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            button_size = 18
        elif 800 < x <= 1200:
            text_size = 12
            button_size = 15
        elif 480 < x <= 800:
            text_size = 10
            button_size = 12
        else:
            text_size = 18
            button_size = 20

        width = self.utils.screen_size()
        qr_width = width - 120
        qr_button = int(qr_width / 2)

        self.address = None
        self.qr_image = None

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
                padding = (0,0,50,0)
            )
        )

        self.address_output = MultilineTextInput(
            style=Pack(
                color=WHITE,
                font_size=text_size,
                text_align=CENTER,
                background_color=rgb(40,43,48),
                font_weight=BOLD,
                padding = (0,10,0,10)
            )
        )
        self.address_output._impl.native.setFocusable(False)
        self.address_output._impl.native.setCursorVisible(False)
        self.address_output._impl.native.setLongClickable(False)
        self.address_output._impl.native.setTextIsSelectable(False)

        self.copy_button = Button(
            text="Copy",
            style=Pack(
                color=BLACK,
                background_color=GREENYELLOW,
                font_size=text_size,
                width=qr_button
            ),
            on_press=self.copy_address
        )

        self.save_button = Button(
            text="Save",
            style=Pack(
                color=BLACK,
                background_color=GREENYELLOW,
                font_size=text_size,
                width=qr_button
            ),
            on_press=self.save_qr
        )

        self.qr_bottons_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(40,43,48),
            )
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
            self.address_output,
            self.qr_bottons_box
        )
        self.qr_bottons_box.add(
            self.save_button,
            self.copy_button
        )

        self.show_qr("transparent")


    def show_qr(self, address_type):
        wallet = self.wallet_storage.get_addresses(address_type)
        if wallet:
            self.address = wallet[0]
            self.qr_image = self.utils.qr_generate(self.address)
            if self.qr_image:
                self.qr_view.image = self.qr_image
                self.address_output.value = self.address


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

    
    async def save_qr(self, button):
        folder_uri_str = await self.main.select_folder.pick_folder()
        if not folder_uri_str:
            ToastMessage("No folder selected")
            return
        if not self.qr_image or not os.path.exists(self.qr_image):
            ToastMessage("No QR image to save")
            return
        context = App.app.current_window._impl.app.native
        try:
            folder_uri = Uri.parse(folder_uri_str)
            folder_doc = DocumentFile.fromTreeUri(context, folder_uri)

            if folder_doc is None or not folder_doc.canWrite():
                ToastMessage("Cannot write to selected folder")
                return

            filename = os.path.basename(self.qr_image)
            existing = folder_doc.findFile(filename)
            if existing:
                existing.delete()

            mime_type = "image/png"
            new_file = folder_doc.createFile(mime_type, filename)
            if new_file is None:
                ToastMessage("Failed to create file")
                return
            resolver = context.getContentResolver()
            output_stream = resolver.openOutputStream(new_file.getUri())
            input_stream = FileInputStream(self.qr_image)
            buffer = bytearray(4096)
            length = input_stream.read(buffer)
            while length > 0:
                output_stream.write(buffer, 0, length)
                length = input_stream.read(buffer)

            input_stream.close()
            output_stream.close()
            ToastMessage(f"Saved to {filename}")
        except Exception as e:
            ToastMessage(f"Error saving file: {e}")


    async def copy_address(self, button):
        CopyText(self.address)