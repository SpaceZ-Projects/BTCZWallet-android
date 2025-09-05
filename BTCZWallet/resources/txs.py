
from datetime import datetime

from toga import App, MainWindow, Box, Label
from ..framework import ClickListener, ToastMessage
from toga.style.pack import Pack
from toga.colors import rgb, GREENYELLOW, RED, WHITE
from toga.constants import ROW, CENTER, BOLD, RIGHT

from .storage import TxsStorage


class Transaction(Box):
    def __init__(self, app:App, main:MainWindow, utils, units, data):
        super().__init__(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
            )
        )

        self.app = app
        self.main = main
        self.units = units
        self.utils = utils

        self.txs_storage = TxsStorage(self.app)
        
        category = data[1]
        self.txid = data[3]
        amount = data[4]
        timestamp = data[7]

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            time_size = 12
        elif 800 < x <= 1200:
            text_size = 12
            time_size = 9
        elif 480 < x <= 800:
            text_size = 10
            time_size = 7
        else:
            text_size = 18
            time_size = 15
        
        if category == "receive":
            text = "Receive"
            color = GREENYELLOW
        elif category == "send":
            text = "Send"
            color = RED
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d\n%H:%M:%S")

        self.category_label = Label(
            text=text,
            style=Pack(
                color=color,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.amount_label = Label(
            text=self.units.format_balance(amount),
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=RIGHT,
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
                flex = 1,
                padding = (17,0,0,0)
            )
        )

        self._impl.native.setOnClickListener(ClickListener(self.show_tx_info))

        self.add(
            self.category_label,
            self.amount_label,
            self.time_label
        )


    def show_tx_info(self, view):
        transaction = self.txs_storage.get_transaction(self.txid)
        tx_type, category, address, txid, amount, blocks, txfee, timestamp = transaction
        if category == "receive":
            text = "Receive"
        elif category == "send":
            text = "Send"
        confirmations = 0
        if blocks > 0:
            try:
                confirmations = (self.main.current_blocks - blocks) + 1
            except Exception:
                ToastMessage("Failed to load transaction")
                return
        message = (
            f"Type : {tx_type}\n"
            f"Category : {text}\n"
            f"Address : {address}\n"
            f"Confirmations : {confirmations}\n\n"
            f"TxID : {txid}\n\n"
            f"Blocks : {blocks}\n"
            f"Amount : {amount}\n"
            f"Fee : {txfee}"
        )
        self.main.info_dialog(
            title="Transaction Info",
            message=message
        )