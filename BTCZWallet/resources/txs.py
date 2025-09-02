
from datetime import datetime

from toga import MainWindow, Box, Label
from ..framework import ClickListener, ToastMessage
from toga.style.pack import Pack
from toga.colors import rgb, GREENYELLOW, RED, WHITE
from toga.constants import ROW, CENTER, BOLD


class Transaction(Box):
    def __init__(self, main:MainWindow, utils, units, data):
        super().__init__(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
            )
        )

        self.main = main
        self.units = units
        self.utils = utils
        
        self.tx_type = data[0]
        category = data[1]
        self.address = data[2]
        self.txid = data[3]
        self.amount = data[4]
        self.blocks = data[5]
        self.txfee = data[6]
        self.timestamp = data[7]

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            time_size = 13
        elif 800 < x <= 1200:
            text_size = 12
            time_size = 10
        elif 480 < x <= 800:
            text_size = 10
            time_size = 8
        else:
            text_size = 18
            time_size = 16

        if category == "mobile_receive":
            text = "Receive"
            color = GREENYELLOW
        elif category == "mobile_send":
            text = "Send"
            color = RED
        self.category = text
        formatted_time = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        self.category_label = Label(
            text=text,
            style=Pack(
                color=color,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                padding = (15,0,0,10)
            )
        )

        self.amount_label = Label(
            text=self.units.format_balance(self.amount),
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.time_label = Label(
            text=formatted_time,
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=time_size,
                text_align=CENTER,
                padding = (15,10,0,0)
            )
        )

        self._impl.native.setOnClickListener(ClickListener(self.show_tx_info))

        self.add(
            self.category_label,
            self.amount_label,
            self.time_label
        )


    def show_tx_info(self, view):
        try:
            confirmations = (self.main.current_blocks - self.blocks) + 1
        except Exception:
            ToastMessage("Failed to load transaction")
            return
        self.main.info_dialog(
            title="Transaction Info",
            message={
                f"Type : {self.tx_type}\n"
                f"Category : {self.category}\n"
                f"Confirmations : {confirmations}\n"
                f"TxID : {self.txid}\n"
                f"Blocks : {self.blocks}\n"
                f"Amount : {self.amount}\n"
                f"Fee : {self.txfee}"
            }
        )