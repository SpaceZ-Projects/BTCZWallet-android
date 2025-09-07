
import asyncio
import operator

from toga import App, MainWindow, Box, ScrollContainer, Label
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD
from toga.colors import rgb, GRAY, YELLOW, WHITE

from .txs import Txid
from .storage import WalletStorage, TxsStorage


class Home(Box):
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

        self.wallet_storage = WalletStorage(self.app)
        self.txs_storage = TxsStorage(self.app)

        self.transactions_data = {}
        self.home_toggle = True

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            total_size = 21
            text_size = 15
        elif 800 < x <= 1200:
            total_size = 18
            text_size = 12
        elif 480 < x <= 800:
            total_size = 16
            text_size = 10
        else:
            total_size = 24
            text_size = 18

        self.status_label = Label(
            text="Status :",
            style=Pack(
                color = GRAY,
                font_size=text_size,
                font_weight=BOLD,
                background_color = rgb(40,43,48),
                padding = (10,0,5,10)
            )
        )

        self.status_value = Label(
            text="",
            style=Pack(
                color = GRAY,
                font_size=text_size,
                font_weight=BOLD,
                background_color = rgb(40,43,48),
                flex = 1,
                padding = (10,0,5,10)
            )
        )

        self.height_label = Label(
            text="Height : NaN",
            style=Pack(
                color=GRAY,
                font_size=text_size,
                background_color = rgb(40,43,48),
                text_align=CENTER,
                padding = (10,10,0,0)
            )
        )

        self.status_box = Box(
            style=Pack(
                direction=ROW,
                background_color = rgb(40,43,48),
                flex = 1
            )
        )

        self.total_label = Label(
            text="Total Balances",
            style=Pack(
                color = WHITE,
                font_size=total_size,
                text_align=CENTER,
                flex = 1,
                padding = (20,0,0,0)
            )
        )

        self.total_value = Label(
            text="0.00000000",
            style=Pack(
                color=WHITE,
                font_size=total_size,
                font_weight=BOLD,
                background_color=rgb(30,33,36),
                text_align=CENTER,
                flex = 1,
                padding = (10,0,0,0)
            )
        )

        self.price_label = Label(
            text="BTCZ Price : NaN",
            style=Pack(
                color=GRAY,
                font_size=text_size,
                background_color=rgb(30,33,36),
                text_align=CENTER,
                padding = (10,0,0,0)
            )
        )

        self.funds_label = Label(
            text="Total : NaN",
            style=Pack(
                color=WHITE,
                font_size=text_size,
                background_color=rgb(30,33,36),
                text_align=CENTER,
                padding = (10,0,0,0)
            )
        )

        self.total_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(30,33,36),
                flex = 2,
                alignment = CENTER
            )
        )

        self.transparent_label = Label(
            text="Transparent",
            style=Pack(
                color = GRAY,
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER
            )
        )

        self.transparent_value = Label(
            text="0.00000000",
            style=Pack(
                color = YELLOW,
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER,
                font_weight=BOLD
            )
        )

        self.transparent_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                flex = 1,
                alignment=CENTER,
                padding = 2
            )
        )

        self.shielded_label = Label(
            text="Shielded",
            style=Pack(
                color = GRAY,
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER
            )
        )

        self.shielded_value = Label(
            text="0.00000000",
            style=Pack(
                color = rgb(114,137,218),
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER,
                font_weight=BOLD
            )
        )

        self.shielded_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(40,43,48),
                flex = 1,
                alignment=CENTER,
                padding = 2
            )
        )

        self.balances_details = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(30,33,36),
                flex = 1,
                alignment = CENTER
            )
        )

        self.balances_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(30,33,36),
                flex = 9,
                alignment=CENTER
            )
        )

        self.wallet_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color = rgb(30,33,36),
                flex = 1.5,
                alignment=CENTER
            )
        )

        self.transactions_scroll = ScrollContainer(
            vertical=True,
            horizontal=False,
            style=Pack(
                background_color = rgb(40,43,48),
                flex=1
            )
        )
        self.transactions_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                alignment=CENTER,
                flex=1
            )
        )
        self.transactions_scroll.content = self.transactions_box

        self.info_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 2,
                alignment=CENTER
            )
        )

        self.add(
            self.wallet_box,
            self.info_box
        )
        self.wallet_box.add(
            self.status_box,
            self.balances_box
        )
        self.status_box.add(
            self.status_label,
            self.status_value,
            self.height_label
        )
        self.balances_box.add(
            self.total_box,
            self.balances_details
        )
        self.total_box.add(
            self.total_label,
            self.total_value,
            self.price_label,
            self.funds_label
        )
        self.balances_details.add(
            self.transparent_box,
            self.shielded_box
        )
        self.transparent_box.add(
            self.transparent_label,
            self.transparent_value
        )
        self.shielded_box.add(
            self.shielded_label,
            self.shielded_value
        )
        self.info_box.add(
            self.transactions_scroll
        )

        asyncio.create_task(self.update_balances())
        asyncio.create_task(self.load_transactions())


    def update_status(self, status, color):
        height, currency, price = self.wallet_storage.get_info()
        self.status_value.style.color = color
        self.status_value.text = status
        self.height_label.text = f"Height : {height}"
        self.price_label.text = f"BTCZ Price : {self.units.format_price(price)} {currency.upper()}"

    
    async def update_balances(self):
        while True:
            _, currency, price = self.wallet_storage.get_info()
            wallet = self.wallet_storage.get_addresses()
            if wallet:
                for data in wallet:
                    tbalance = data[2]
                    zbalance = data[3]
                    total_balances = tbalance + zbalance
                    self.transparent_value.text = self.units.format_balance(tbalance)
                    self.shielded_value.text = self.units.format_balance(zbalance)
                    self.total_value.text = self.units.format_balance(total_balances)
                    total_funds = total_balances * float(price)
                    self.funds_label.text = f"Total : {self.units.format_price(total_funds)} {currency.upper()}"
                    self.main.tbalance = tbalance
                    self.main.zbalance = zbalance
                
            await asyncio.sleep(5)


    async def load_transactions(self):
        transactions = self.txs_storage.get_transactions()
        transactions = sorted(
            transactions,
            key=operator.itemgetter(7),
            reverse=True
        )
        for data in transactions[:20]:
            txid = data[3]
            transaction_info = Txid(self.app, self.main, self.script_path, self.utils, self.units, data)
            self.transactions_data[txid] = transaction_info
            self.transactions_box.add(transaction_info)
            await asyncio.sleep(0.0)

        await asyncio.sleep(1)
        asyncio.create_task(self.update_transactions())


    async def update_transactions(self):
        while True:
            if not self.home_toggle:
                await asyncio.sleep(1)
                continue
            height = self.wallet_storage.get_info("height")
            transactions = self.txs_storage.get_transactions()
            transactions = sorted(
                transactions,
                key=operator.itemgetter(7),
                reverse=False
            )
            for data in transactions[20:]:
                tx_type = data[0]
                txid = data[3]
                blocks = data[5]
                if txid not in self.transactions_data:
                    transaction_info = Txid(self.app, self.main, self.script_path, self.utils, self.units, data)
                    self.transactions_data[txid] = transaction_info
                    self.transactions_box.insert(0, transaction_info)
                    if len(self.transactions_data) > 20:
                        child = self.transactions_box.children[20]
                        self.transactions_box.remove(child)
                    await asyncio.sleep(0.0)
                else:
                    confirmations = 0
                    existing_tx = self.transactions_data[txid]
                    if blocks > 0:
                        if tx_type == "shielded":
                            confirmations = height[0] - blocks
                        else:
                            confirmations = (height[0] - blocks) + 1
                    if confirmations <= 6:
                        icon = f"{self.script_path}/images/{confirmations}.png"
                    else:
                        icon = f"{self.script_path}/images/6.png"
                    existing_tx.confirmations_icon.image = icon

            
            await asyncio.sleep(5)