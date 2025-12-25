
import asyncio

from toga import (
    App, MainWindow, Box, Label, ScrollContainer, Switch,
    Button, TextInput, ImageView, NumberInput, Slider
)
from ..framework import (
    ClickListener, ToastMessage, InputType, FocusChangeListener,
    RelativeDialog
)
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, GRAY, YELLOW, WHITE, BLACK, RED, GREENYELLOW

from .book import AddressBook
from .storage import DeviceStorage, AddressesStorage


class CashOut(RelativeDialog):
    def __init__(self, app:App, script_path, utils, units, info, title=None, cancelable=False):
        super().__init__(app.activity, title, cancelable, view_space=20)

        self.script_path = script_path

        tx_type = info[0]
        address = info[1]
        amount = info[2]
        txfee = info[3]

        x = utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            address_size = 13
        elif 800 < x <= 1200:
            text_size = 12
            address_size = 10
        elif 480 < x <= 800:
            text_size = 10
            address_size = 8
        else:
            text_size = 18
            address_size = 16

        self.tx_type_label = Label(
            text=f"Type : {tx_type}",
            style=Pack(
                color= WHITE,
                font_weight=BOLD,
                font_size= text_size
            )
        )

        self.address_label = Label(
            text="Destination",
            style=Pack(
                color= GRAY,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.address_value = Label(
            text=address,
            style=Pack(
                color= WHITE,
                font_size = address_size
            )
        )

        self.amount_label = Label(
            text=f"Amount : {units.format_balance(amount)}",
            style=Pack(
                color= WHITE,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.txfee_label = Label(
            text=f"Txfee : {units.format_balance(txfee)}",
            style=Pack(
                color= WHITE,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.cashout_status = Label(
            text=f"",
            style=Pack(
                color= YELLOW,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.cashout_success = ImageView(
            image=f"{self.script_path}/images/confirmed.png",
            style=Pack(
                width = 120,
                height= 120
            )
        )

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = WHITE,
                background_color = RED
            ),
            on_press=self.cancel_cashout
        )

        self.confirm_button = Button(
            text="Confim",
            style=Pack(
                color = BLACK,
                background_color = GREENYELLOW
            )
        )

        self.buttons_box = Box(
            style=Pack(
                direction=ROW
            )
        )
        self.buttons_box.add(
            self.cancel_button,
            self.confirm_button
        )
        self.add(
            self.tx_type_label,
            self.address_label,
            self.address_value,
            self.amount_label,
            self.txfee_label,
            self.buttons_box
        )


    def disable_buttons(self):
        self.remove(self.buttons_box)
        self.cashout_status.text = "Processing..."
        self.add(self.cashout_status)


    def enable_buttons(self):
        self.remove(self.cashout_status)
        self.add(self.buttons_box)

    async def succeed(self):
        self.remove(
            self.tx_type_label,
            self.address_label,
            self.address_value,
            self.amount_label,
            self.txfee_label
        )
        self.cashout_status.text = "Success"
        self.add(self.cashout_success)
        await asyncio.sleep(3)
        self.hide()


    def cancel_cashout(self, button):
        self.hide()


class Send(Box):
    def __init__(self, app:App, main:MainWindow, script_path, utils, units):
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

        self.device_storage = DeviceStorage(self.app)
        self.addresses_storage = AddressesStorage(self.app)

        self.book_toggle = None

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            self.text_size = 15
            switch_size = 17
            button_size = 18
            input_size = 18
            icon_width = 35
        elif 800 < x <= 1200:
            self.text_size = 12
            switch_size = 14
            button_size = 15
            input_size = 15
            icon_width = 30
        elif 480 < x <= 800:
            self.text_size = 10
            switch_size = 11
            button_size = 12
            input_size = 12
            icon_width = 25
        else:
            self.text_size = 18
            switch_size = 19
            button_size = 20
            input_size = 20
            icon_width = 40

        self.orientation_toggle = None

        self.switch_type = Switch(
            text="Transparent",
            value=False,
            style=Pack(
                color=YELLOW,
                background_color=rgb(30,33,36),
                font_size=switch_size,
                font_weight=BOLD,
                flex= 1,
                padding=10
            ),
            on_change=self.switch_sending_type
        )

        self.current_balance_label = Label(
            text="Balance : 0.00000000",
            style=Pack(
                color=YELLOW,
                background_color=rgb(30,33,36),
                font_size=self.text_size,
                font_weight=BOLD,
                flex = 1,
                padding = (0,0,5,10)
            )
        )

        self.switch_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
                padding = 10
            )
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
        self.destination_input._impl.native.setShowSoftInputOnFocus(False)

        self.address_book = ImageView(
            image=f"{self.script_path}/images/book_w.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width=icon_width,
                padding = (8,10,0,0)
            )
        )
        self.address_book._impl.native.setClickable(True)
        self.address_book._impl.native.setOnClickListener(ClickListener(self.show_address_book))

        self.scan_address = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(40,43,48),
                width=icon_width,
                padding = (8,10,0,0)
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

        self.btcz_icon = ImageView(
            image=f"{self.script_path}/images/BitcoinZ-round-48.png",
            style=Pack(
                background_color=rgb(40,43,48),
                width=icon_width,
                padding = (15,0,0,10)
            )
        )

        self.amount_input = NumberInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_size=input_size,
                text_align=CENTER,
                flex = 1.5,
                padding = (10,10,0,10)
            ),
            on_change=self.check_balance
        )
        self.amount_input._impl.native.setInputType(
            InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL
        )
        self.amount_input._impl.native.setOnFocusChangeListener(FocusChangeListener(self.on_focus_change))

        self.check_amount_label = Label(
            text="",
            style=Pack(
                background_color=rgb(40,43,48),
                font_size=self.text_size,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 70,
                alignment=CENTER
            )
        )

        self.amount_slider = Slider(
            min=0,
            max=100,
            value=0,
            tick_count=5,
            style=Pack(
                flex = 3.5
            ),
            on_change=self.on_slider_change
        )

        self.slider_percentage = Label(
            text="%0",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_size=self.text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex= 1
            )
        )

        self.amount_slider_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 45,
                alignment=CENTER
            )
        )

        self.fee_label = Label(
            text="Fee :",
            style=Pack(
                color=GRAY,
                background_color=rgb(40,43,48),
                font_size=self.text_size,
                font_weight=BOLD,
                padding = (15,32,0,10)
            )
        )

        self.fee_input = NumberInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(30,33,36),
                font_size=input_size,
                text_align=CENTER,
                flex= 1.5,
                padding = (10,10,0,10)
            )
        )
        self.fee_input._impl.native.setInputType(
            InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL
        )
        self.fee_input._impl.native.setText("0.00001000")
        self.fee_input._impl.native.setOnFocusChangeListener(FocusChangeListener(self.on_focus_change))

        self.empty_label = Label(
            text="",
            style=Pack(
                background_color=rgb(40,43,48),
                font_size=self.text_size,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.fee_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                height = 70,
                alignment=CENTER
            )
        )

        self.options_scroll = ScrollContainer(
            vertical=True,
            horizontal=False,
            style=Pack(
                background_color=rgb(40,43,48),
                flex = 7,
                padding=(0,10,0,10)
            )
        )

        self.options_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(40,43,48),
                flex = 1
            )
        )
        self.options_scroll.content = self.options_box

        self.send_button = Button(
            text="Cashout",
            enabled=False,
            style=Pack(
                color=WHITE,
                background_color=GRAY,
                font_size=button_size,
                padding=10
            ),
            on_press=self.check_inputs
        )

        self.send_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color = rgb(40,43,48),
                flex=2
            )
        )

        self.add(
            self.switch_box,
            self.options_scroll,
            self.send_box
        )
        self.switch_box.add(
            self.switch_type,
            self.current_balance_label
        )
        self.options_box.add(
            self.destination_box,
            self.amount_box,
            self.amount_slider_box,
            self.fee_box
        )
        self.destination_box.add(
            self.destination_input,
            self.address_book,
            self.scan_address
        )
        self.amount_box.add(
            self.btcz_icon,
            self.amount_input,
            self.check_amount_label
        )
        self.amount_slider_box.add(
            self.amount_slider,
            self.slider_percentage
        )
        self.fee_box.add(
            self.fee_label,
            self.fee_input,
            self.empty_label
        )
        self.send_box.add(
            self.send_button
        )


    def update_balance(self):
        if self.switch_type.value is False:
            if self.main.tbalance:
                self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.tbalance)}"
        else:
            if self.main.zbalance:
                self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.zbalance)}"


    def adjust_size(self):
        if not self.orientation_toggle:
            self.options_scroll.style.flex = 1
            self.send_box.style.flex = 0
            self.orientation_toggle = True

    
    async def switch_sending_type(self, switch):
        if switch.value is True:
            self.switch_type.style.color = rgb(114,137,218)
            self.switch_type.text = "Shielded"
            self.current_balance_label.style.color = rgb(114,137,218)
            self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.zbalance)}"
            if self.destination_input.value and self.amount_input.value:
                self.send_button.style.color = BLACK
                self.send_button.style.background_color = rgb(114,137,218)
                self.send_button.enabled = True
            else:
                self.send_button.style.color = WHITE
                self.send_button.style.background_color = GRAY
                self.send_button.enabled = False
        else:
            self.switch_type.style.color = YELLOW
            self.switch_type.text = "Transparent"
            self.current_balance_label.style.color = YELLOW
            self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.tbalance)}"
            if self.destination_input.value and self.amount_input.value:
                self.send_button.style.color = BLACK
                self.send_button.style.background_color = YELLOW
                self.send_button.enabled = True
            else:
                self.send_button.style.color = WHITE
                self.send_button.style.background_color = GRAY
                self.send_button.enabled = False
                
        self.amount_input.value = ""
        self.amount_slider.value = 0


    def show_address_book(self, view):
        if not self.book_toggle:
            self.book_toggle = True
            self.book_dialog = AddressBook(self.app, self.main, self.script_path, self.utils, self.units, True, self)
            self.options_box.insert(1, self.book_dialog)
            self.app.loop.create_task(self.book_dialog.load_address_book())
        else:
            self.hide_address_book()

    def hide_address_book(self):
        self.options_box.remove(self.book_dialog)
        self.book_toggle = None

    
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


    async def check_address(self, input):
        if input.value:
            if self.switch_type.value is False:
                if self.amount_input.value:
                    self.send_button.style.color = BLACK
                    self.send_button.style.background_color = YELLOW
                    self.send_button.enabled = True
            else:
                if self.amount_input.value:
                    self.send_button.style.color = BLACK
                    self.send_button.style.background_color = rgb(114,137,218)
                    self.send_button.enabled = True
        else:
            self.send_button.style.color = WHITE
            self.send_button.style.background_color = GRAY
            self.send_button.enabled = False


    async def check_balance(self, input):
        edittext = self.amount_input._impl.native
        value = edittext.getText().toString().strip()
        if value:
            amount = float(value)
            if self.switch_type.value is False:
                if amount >= self.main.tbalance:
                    self.check_amount_label.style.color = RED
                    self.check_amount_label.text = "Insufficient"
                else:
                    self.check_amount_label.text = ""
                if self.destination_input.value:
                    self.send_button.style.color = BLACK
                    self.send_button.style.background_color = YELLOW
                    self.send_button.enabled = True
            else:
                if amount >= self.main.zbalance:
                    self.check_amount_label.style.color = RED
                    self.check_amount_label.text = "Insufficient"
                else:
                    self.check_amount_label.text = ""
                if self.destination_input.value:
                    self.send_button.style.color = BLACK
                    self.send_button.style.background_color = rgb(114,137,218)
                    self.send_button.enabled = True
        else:
            self.send_button.style.color = WHITE
            self.send_button.style.background_color = GRAY
            self.send_button.enabled = False


    async def check_inputs(self, button):
        self.address = self.destination_input.value.strip()
        self.amount = float(self.amount_input._impl.native.getText().toString().strip())
        self.txfee = float(self.fee_input._impl.native.getText().toString().strip())
        total_amount = self.amount + self.txfee
        if self.switch_type.value is False:
            self.tx_type = "transparent"
            if total_amount > self.main.tbalance:
                self.main.error_dialog(
                    title="Insufficient Funds",
                    message=f"Total {total_amount} exceeds your transparent balance ({self.main.tbalance})."
                )
                return
        else:
            self.tx_type = "shielded"
            if total_amount > self.main.zbalance:
                self.main.error_dialog(
                    title="Insufficient Funds",
                    message=f"Total {total_amount} exceeds your shielded balance ({self.main.zbalance})."
                )
                return
        info = [
            self.tx_type,
            self.address,
            self.amount,
            self.txfee
        ]
        self.cashout_dialog = CashOut(self.app, self.script_path, self.utils, self.units, info)
        self.cashout_dialog.confirm_button.on_press = self.confirm_cashout
        self.cashout_dialog.show()


    async def confirm_cashout(self, button):
        self.cashout_dialog.disable_buttons()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/cashout'
        params = {
            "type": self.tx_type,
            "address": self.address,
            "amount": self.amount,
            "fee": self.txfee
        }
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.cashout_dialog.enable_buttons()
        elif result and "error" in result:
            self.cashout_dialog.hide()
            error_message = result.get('error')
            self.main.error_dialog(
                title="Cashout Failed",
                message=error_message
            )
        else:
            await self.cashout_dialog.succeed()
            self.destination_input.value = ""
            self.amount_input.value = ""

            
    def on_slider_change(self, slider):
        percent = int(slider.value)
        self.slider_percentage.text = f"%{percent}"
        if self.switch_type.value is False:
            balance = self.main.tbalance
        else:
            balance = self.main.zbalance
        amount = (percent / 100) * balance
        if percent == 100:
            amount -= 0.00001
        elif percent == 0:
            self.amount_input.value = ""
            return
        formatted = self.units.format_balance(amount)
        self.amount_input._impl.native.setText(formatted)

    
    def on_focus_change(self, v, has_focus):
        if has_focus:
            self.adjust_size()
        else:
            value = self.fee_input._impl.native.getText().toString().strip()
            if not value:
                self.fee_input._impl.native.setText("0.00001000")