
import asyncio

from toga import (
    App, MainWindow, Box, Label, ScrollContainer, TextInput,
    Button, ImageView
)
from ..framework import ToastMessage, ClickListener, CopyText
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW
from toga.colors import rgb, GRAY, WHITE, YELLOW, GREENYELLOW, BLACK, TRANSPARENT

from .storage import DeviceStorage, AddressesStorage



class Address(Box):
    def __init__(self, script_path, utils, data, option=None, send_page=None):
        super().__init__(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
            )
        )

        self.script_path = script_path
        self.utils = utils
        
        self.name = data[0]
        self.address = data[1]

        self.option = option
        self.send_page = send_page

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 16
            icon_width = 35
        elif 800 < x <= 1200:
            text_size = 13
            icon_width = 30
        elif 480 < x <= 800:
            text_size = 11
            icon_width = 25
        else:
            text_size = 19
            icon_width = 40

        self.contact_icon = ImageView(
            image=f"{self.script_path}/images/contact.png",
            style=Pack(
                background_color=rgb(20,20,20),
                height = icon_width,
                padding=(10,0,0,5),
                alignment=CENTER
            )
        )

        self.name_label = Label(
            text=self.name,
            style=Pack(
                color=WHITE,
                font_size=text_size,
                font_weight=BOLD,
                background_color=rgb(20,20,20),
                text_align=CENTER,
                flex=1,
                padding = (15,0,0,0)
            )
        )

        self._impl.native.setClickable(True)
        self._impl.native.setOnClickListener(ClickListener(self.copy_address))

        self.add(
            self.contact_icon,
            self.name_label
        )
        

    def copy_address(self, view):
        if self.option:
            self.send_page.destination_input.value = self.address
            self.send_page.hide_address_book()
        else:
            CopyText(self.address)



class AddressBook(Box):
    def __init__(self, app:App, main:MainWindow, script_path, utils, units, option=None, send_page=None):
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
        self.script_path = script_path
        self.utils = utils
        self.units = units
        self.option = option
        self.send_page = send_page

        self.device_storage = DeviceStorage(self.app)
        self.addresses_storage = AddressesStorage(self.app)

        self.book_toggle = None
        self.addresses_data = {}

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            title_size = 20
            text_size = 14
            input_size = 18
            icon_width = 37
        elif 800 < x <= 1200:
            title_size = 17
            text_size = 11
            input_size = 15
            icon_width = 37
        elif 480 < x <= 800:
            title_size = 14
            text_size = 9
            input_size = 12
            icon_width = 33
        else:
            title_size = 23
            text_size = 17
            input_size = 20
            icon_width = 40


        self.add_button = Button(
            text="+ Add",
            style=Pack(
                color=BLACK,
                font_size=text_size,
                background_color=YELLOW,
                font_weight=BOLD,
                flex = 1
            ),
            on_press=self.show_inputs
        )

        self.title_label = Label(
            text="Address Book",
            style=Pack(
                color = GRAY,
                background_color = rgb(30,33,36),
                font_weight=BOLD,
                font_size=title_size,
                text_align=CENTER,
                flex = 1
            )
        )

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(30,33,36),
                alignment=CENTER,
                padding = (5,5,5,5)
            )
        )

        self.name_input = TextInput(
            placeholder="Enter name",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_change=self.check_name
        )

        self.destination_input = TextInput(
            placeholder="Enter address",
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_change=self.check_address
        )

        self.scan_address = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width=icon_width,
                padding = (7,10,0,0)
            )
        )
        self.scan_address._impl.native.setClickable(True)
        self.scan_address._impl.native.setOnClickListener(ClickListener(self.scan_qr_address))

        self.destination_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 70,
                alignment=CENTER
            )
        )

        self.confirm_button = Button(
            text="Confirm",
            enabled=False,
            style=Pack(
                color=BLACK,
                font_size=text_size,
                background_color=GRAY,
                font_weight=BOLD,
                flex = 1,
                padding = (0,10,5,10)
            ),
            on_press=self.add_address
        )

        self.inputs_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER
            )
        )

        self.book_list = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
                flex=1
            )
        )

        self.book_scroll = ScrollContainer(
            style=Pack(
                background_color=rgb(30,33,36),
                flex=1
            )
        )

        self.book_scroll.content = self.book_list

        if option:
            self.add(
            self.book_scroll
            )
        else:
            self.add(
                self.menu_box,
                self.book_scroll
            )
            self.menu_box.add(
                self.add_button,
                self.title_label
            )
            self.inputs_box.add(
                self.name_input,
                self.destination_box,
                self.confirm_button
            )
            self.destination_box.add(
                self.destination_input,
                self.scan_address
            )


    def run_book_task(self):
        if not self.book_toggle:
            self.book_toggle = True
            self.app.loop.create_task(self.load_address_book())


    async def load_address_book(self):
        address_book = self.addresses_storage.get_address_book()
        for data in address_book:
            address = data[1]
            address_info = Address(self.script_path, self.utils, data, self.option, self.send_page)
            self.addresses_data[address] = address_info
            self.book_list.add(address_info)
            await asyncio.sleep(0.0)

        if not self.option:
            await asyncio.sleep(1)
            self.app.loop.create_task(self.update_address_book())


    async def update_address_book(self):
        local_addresses = []
        while True:
            address_book = self.addresses_storage.get_address_book()
            for data in address_book:
                address = data[1]
                local_addresses.append(address)
                if address not in self.addresses_data:
                    address_info = Address(self.script_path, self.utils, data)
                    self.addresses_data[address] = address_info
                    self.book_list.add(address_info)
                    await asyncio.sleep(0.0)
            
            for address in self.addresses_data:
                if address not in local_addresses:
                    existing_address = self.addresses_data[address]
                    self.book_list.remove(existing_address)

            local_addresses.clear()
            
            await asyncio.sleep(5)


    def show_inputs(self, button):
        button.text = "- Cancel"
        button.style.color = WHITE
        button.style.background_color = GRAY
        self.insert(1, self.inputs_box)
        button.on_press = self.hide_inputs

    
    def hide_inputs(self, button):
        button.text = "+ Add"
        button.style.color = BLACK
        button.style.background_color = YELLOW
        self.name_input.value = ""
        self.destination_input.value = ""
        self.remove(self.inputs_box)
        button.on_press = self.show_inputs


    async def check_address(self, input):
        if input.value:
            if self.name_input.value:
                self.confirm_button.style.color = BLACK
                self.confirm_button.style.background_color = GREENYELLOW
                self.confirm_button.enabled = True
        else:
            self.confirm_button.style.color = WHITE
            self.confirm_button.style.background_color = GRAY
            self.confirm_button.enabled = False


    async def check_name(self, input):
        if input.value:
            if self.destination_input.value:
                self.confirm_button.style.color = BLACK
                self.confirm_button.style.background_color = GREENYELLOW
                self.confirm_button.enabled = True
        else:
            self.confirm_button.style.color = WHITE
            self.confirm_button.style.background_color = GRAY
            self.confirm_button.enabled = False

    
    def scan_qr_address(self, view):
        asyncio.ensure_future(self.handle_scan())


    async def handle_scan(self):
        result = await self.main.qr_scanner.start_scan(15)
        if result == "__TIMEOUT__":
            ToastMessage("The scanner was timeout")
        elif result:
            self.destination_input.value = result
        else:
            ToastMessage("No result")


    async def add_address(self, button):
        self.disable_buttons()
        name = self.name_input.value.strip()
        address = self.destination_input.value.strip()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/book'
        params = {
            "name": name,
            "address": address
        }
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.enable_buttons()
        elif result and "error" in result:
            self.enable_buttons()
            error_message = result.get('error')
            self.main.error_dialog(
                title="Add Failed",
                message=error_message
            )
        else:
            self.addresses_storage.insert_book(name, address)
            self.enable_buttons()
            self.name_input.value = ""
            self.destination_input.value = ""
            self.main.info_dialog(
                title="Add Succeed",
                message=f"Name : {name}\nAddress : {address}"
            )


    def disable_buttons(self):
        self.confirm_button.text = "Processing..."
        self.confirm_button.style.color = WHITE
        self.confirm_button.style.background_color = GRAY
        self.add_button.enabled = False
        self.confirm_button.enabled = False


    def enable_buttons(self):
        self.confirm_button.text = "Confirm"
        self.confirm_button.style.color = BLACK
        self.confirm_button.style.background_color = GREENYELLOW
        self.add_button.enabled = True
        self.confirm_button.enabled = True