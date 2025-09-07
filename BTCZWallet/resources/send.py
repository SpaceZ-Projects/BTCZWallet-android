
import asyncio

from toga import App, MainWindow, Box, Label, ScrollContainer, Switch, Button, TextInput, ImageView, NumberInput
from ..framework import ClickListener, ToastMessage, InputType, FocusChangeListener
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, GRAY, YELLOW, WHITE, BLACK, RED

from .storage import DeviceStorage


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

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            switch_size = 17
            button_size = 18
            input_size = 18
            icon_width = 37
        elif 800 < x <= 1200:
            text_size = 12
            switch_size = 14
            button_size = 15
            input_size = 15
            icon_width = 37
        elif 480 < x <= 800:
            text_size = 10
            switch_size = 11
            button_size = 12
            input_size = 12
            icon_width = 33
        else:
            text_size = 18
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
                font_size=text_size,
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
                background_color = rgb(40,43,48),
                font_size=input_size,
                text_align=CENTER,
                flex = 1,
                padding = (10,10,0,10)
            ),
            on_gain_focus=self.on_gain_focus,
            on_change=self.check_address
        )

        self.scan_address = ImageView(
            image=f"{self.script_path}/images/qrscanner.png",
            style=Pack(
                background_color = rgb(66,69,73),
                width=icon_width,
                padding = (7,10,0,0)
            )
        )
        self.scan_address._impl.native.setClickable(True)
        self.scan_address._impl.native.setOnClickListener(ClickListener(self.scan_qr_address))

        self.destination_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 70,
                alignment=CENTER
            )
        )

        self.amount_label = Label(
            text="Amount :",
            style=Pack(
                color=GRAY,
                background_color=rgb(66,69,73),
                font_size=text_size,
                font_weight=BOLD,
                padding = (15,0,0,10)
            )
        )

        self.amount_input = NumberInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
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
                background_color=rgb(66,69,73),
                font_size=text_size,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 70,
                alignment=CENTER
            )
        )

        self.fee_label = Label(
            text="Fee :",
            style=Pack(
                color=GRAY,
                background_color=rgb(66,69,73),
                font_size=text_size,
                font_weight=BOLD,
                padding = (15,32,0,10)
            )
        )

        self.fee_input = NumberInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
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
                background_color=rgb(66,69,73),
                font_size=text_size,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.fee_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(66,69,73),
                height = 70,
                alignment=CENTER
            )
        )

        self.options_scroll = ScrollContainer(
            vertical=True,
            horizontal=False,
            style=Pack(
                background_color=rgb(30,33,36),
                flex = 7,
                padding=(0,10,0,10)
            )
        )

        self.options_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
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
            self.fee_box
        )
        self.destination_box.add(
            self.destination_input,
            self.scan_address
        )
        self.amount_box.add(
            self.amount_label,
            self.amount_input,
            self.check_amount_label
        )
        self.fee_box.add(
            self.fee_label,
            self.fee_input,
            self.empty_label
        )
        self.send_box.add(
            self.send_button
        )

        asyncio.create_task(self.update_balance())


    async def update_balance(self):
        while True:
            if self.switch_type.value is False:
                if self.main.tbalance:
                    self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.tbalance)}"
            else:
                if self.main.zbalance:
                    self.current_balance_label.text = f"Balance : {self.units.format_balance(self.main.zbalance)}"

            await asyncio.sleep(5)


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
        address = self.destination_input.value.strip()
        amount = float(self.amount_input._impl.native.getText().toString().strip())
        txfee = float(self.fee_input._impl.native.getText().toString().strip())
        total_amount = amount + txfee
        if self.switch_type.value is False:
            tx_type = "transparent"
            if total_amount > self.main.tbalance:
                self.main.error_dialog(
                    title="Insufficient Funds",
                    message=f"Total {total_amount} exceeds your transparent balance ({self.main.tbalance})."
                )
                return
        else:
            tx_type = "shielded"
            if total_amount > self.main.zbalance:
                self.main.error_dialog(
                    title="Insufficient Funds",
                    message=f"Total {total_amount} exceeds your shielded balance ({self.main.zbalance})."
                )
                return
        self.switch_type.enabled = False
        self.scan_address._impl.native.setOnClickListener(None)
        self.send_button.enabled = False
        self.send_button.text = "Processing..."
        self.destination_input.enabled = False
        self.amount_input.enabled = False
        self.fee_input.enabled = False
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/cashout'
        params = {
            "type": tx_type,
            "address": address,
            "amount": amount,
            "fee": txfee
        }
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
        elif result and "error" in result:
            error_message = result.get('error')
            self.main.error_dialog(
                title="Cashout Failed",
                message=error_message
            )
        else:
            txid = result.get('txid')
            self.main.info_dialog(
                title="Sent",
                message=f"TxID : {txid}"
            )
            self.destination_input.value = ""
            self.amount_input.value = ""

        self.switch_type.enabled = True
        self.scan_address._impl.native.setOnClickListener(ClickListener(self.scan_qr_address))
        self.send_button.enabled = True
        self.send_button.text = "Cashout"
        self.destination_input.enabled = True
        self.amount_input.enabled = True
        self.fee_input.enabled = True
            
                 

    def on_gain_focus(self, input):
        self.adjust_size()

    
    def on_focus_change(self, v, has_focus):
        if has_focus:
            self.adjust_size()
        
        if not self.fee_input.value:
            self.fee_input._impl.native.setText("0.00001000")