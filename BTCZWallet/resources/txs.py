
import asyncio
from datetime import datetime
import operator

from toga import App, MainWindow, Box, Label, ImageView, ScrollContainer
from ..framework import (
    ClickListener, LongClickListener, PopupMenu, BitmapDrawable,
    BitmapFactory, MenuClickListener, Boolean, Intent, Uri,
    CopyText
)
from toga.style.pack import Pack
from toga.colors import rgb, GREENYELLOW, RED, WHITE
from toga.constants import ROW, CENTER, BOLD, RIGHT, COLUMN

from .storage import TxsStorage, WalletStorage


class Txid(Box):
    def __init__(self, app:App, main:MainWindow, script_path, utils, units, data):
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
        self.script_path = script_path
        self.units = units
        self.utils = utils

        self.txs_storage = TxsStorage(self.app)
        self.wallet_storage = WalletStorage(self.app)

        self.has_confirmed = None
        
        tx_type = data[0]
        category = data[1]
        self.txid = data[3]
        self.amount = data[4]
        blocks = data[5]
        timestamp = data[7]

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
            time_size = 12
            category_size = 13
            conf_height = 40
        elif 800 < x <= 1200:
            text_size = 12
            time_size = 9
            category_size = 10
            conf_height = 40
        elif 480 < x <= 800:
            text_size = 10
            time_size = 7
            category_size = 8
            conf_height = 35
        else:
            text_size = 18
            time_size = 15
            category_size = 16
            conf_height = 45
        
        if category == "receive":
            text = "Receive"
            color = GREENYELLOW
        elif category == "send":
            text = "Send"
            color = RED
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d\n%H:%M:%S")

        confirmations = 0
        height = self.wallet_storage.get_info("height")
        if blocks > 0:
            if tx_type == "shielded":
                confirmations = height[0] - blocks
            else:
                confirmations = (height[0] - blocks) + 1
        if 0 <= confirmations <= 6:
            icon = f"{self.script_path}/images/{confirmations}.png"
        elif confirmations < 0:
            icon = f"{self.script_path}/images/0.png"
        else:
            icon = f"{self.script_path}/images/confirmed.png"
            self.has_confirmed = True

        self.confirmations_icon = ImageView(
            image=icon,
            style=Pack(
                background_color=rgb(20,20,20),
                height = conf_height,
                padding=(10,0,0,5),
                alignment=CENTER
            )
        )

        self.category_label = Label(
            text=text,
            style=Pack(
                color=color,
                background_color=rgb(20,20,20),
                font_size=category_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.amount_label = Label(
            text=self.units.format_balance(self.amount),
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

        self._impl.native.setClickable(True)
        self._impl.native.setOnClickListener(ClickListener(self.show_tx_info))
        self._impl.native.setOnLongClickListener(LongClickListener(self.show_txid_popmenu))

        self.add(
            self.confirmations_icon,
            self.category_label,
            self.amount_label,
            self.time_label
        )


    def show_tx_info(self, view):
        height = self.wallet_storage.get_info("height")
        transaction = self.txs_storage.get_transaction(self.txid, self.amount)
        tx_type, category, address, txid, amount, blocks, txfee, timestamp = transaction
        if category == "receive":
            text = "Receive"
        elif category == "send":
            text = "Send"
        confirmations = 0
        if blocks > 0:
            if tx_type == "shielded":
                confirmations = height[0] - blocks
            else:
                confirmations = (height[0] - blocks) + 1
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"Type : {tx_type}\n"
            f"Category : {text}\n"
            f"Address : {address}\n"
            f"Confirmations : {confirmations}\n\n"
            f"TxID : {txid}\n\n"
            f"Blocks : {blocks}\n"
            f"Amount : {amount}\n"
            f"Fee : {txfee}\n\n"
            f"Date : {formatted_time}"
        )
        self.main.info_dialog(
            title="Transaction Info",
            message=message
        )


    def show_txid_popmenu(self, view):
        popup = PopupMenu(self.app.activity, view)
        context_menu = popup.getMenu()

        copy_txid_cmd = context_menu.add("Copy Txid")
        copy_icon = f"{self.script_path}/images/copy.png"
        copy_bmp = BitmapFactory.decodeFile(copy_icon)
        copy_drawable = BitmapDrawable(self.app.activity.getResources(), copy_bmp)
        copy_txid_cmd.setIcon(copy_drawable)

        explorer_cmd = context_menu.add("Open in explorer")
        explorer_icon = f"{self.script_path}/images/explorer.png"
        explorer_bmp = BitmapFactory.decodeFile(explorer_icon)
        explorer_drawable = BitmapDrawable(self.app.activity.getResources(), explorer_bmp)
        explorer_cmd.setIcon(explorer_drawable)

        try:
            popup_class = popup.getClass()
            field = popup_class.getDeclaredField("mPopup")
            field.setAccessible(True)
            menu_helper = field.get(popup)
            menu_helper_class = menu_helper.getClass()
            method = menu_helper_class.getDeclaredMethod("setForceShowIcon", Boolean.TYPE)
            method.invoke(menu_helper, True)
        except Exception as e:
            print(f"error icon: {e}")

        popup.setOnMenuItemClickListener(MenuClickListener(self.on_popmenu_click))
        popup.show()


    def on_popmenu_click(self, title):
        if title == "Open in explorer":
            url = f"https://explorer.btcz.rocks/tx/{self.txid}"
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            intent.addCategory(Intent.CATEGORY_BROWSABLE)
            self.app.activity.startActivity(intent)

        elif title == "Copy Txid":
            CopyText(self.txid)
        



class Transactions(ScrollContainer):
    def __init__(self, app:App, main:MainWindow, script_path, utils, units):
        super().__init__()

        self.vertical=True
        self.horizontal=False
        self.on_scroll = self._handle_on_scroll

        self.app = app
        self.main = main
        self.script_path = script_path
        self.utils = utils
        self.units = units

        self.txs_storage = TxsStorage(self.app)
        self.wallet_storage = WalletStorage(self.app)

        self.transactions_data = {}
        self.no_more_transactions = None
        self.scroll_toggle = None
        self.is_loading = None

        self.transactions_count = 20
        self.transactions_from = 0

        self.transactions_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment=CENTER
            )
        )

        self.content = self.transactions_box


    def get_transactions(self, limit, offset):
        transactions_list = self.txs_storage.get_transactions()
        if not transactions_list:
            return []
        sorted_transactions = sorted(
            transactions_list,
            key=operator.itemgetter(7),
            reverse=True
        )
        transactions = sorted_transactions[offset:offset + limit]
        return transactions


    async def update_transactions(self):
        height = self.wallet_storage.get_info("height")
        transactions = self.get_transactions(20, 0)
        transactions = sorted(
            transactions,
            key=operator.itemgetter(7),
            reverse=False
        )
        def normalize_stored(data):
            return (
                data[0],
                data[1],
                data[2],
                data[3],
                float(data[4]),
                int(data[7]),
            )
        for data in transactions:
            tx_type = data[0]
            blocks = data[5]
            key = normalize_stored(data)
            if key not in self.transactions_data:
                transaction_info = Txid(self.app, self.main, self.script_path, self.utils, self.units, data)
                self.transactions_box.insert(0, transaction_info)
                self.transactions_data[key] = transaction_info
                await asyncio.sleep(0.0)
            else:
                confirmations = 0
                existing_tx = self.transactions_data[key]
                if blocks > 0:
                    if tx_type == "shielded":
                        confirmations = height[0] - blocks
                    else:
                        confirmations = (height[0] - blocks) + 1
                if 0 <= confirmations <= 6:
                    icon = f"{self.script_path}/images/{confirmations}.png"
                    existing_tx.confirmations_icon.image = icon
                elif confirmations < 0:
                    icon = f"{self.script_path}/images/0.png"
                    existing_tx.confirmations_icon.image = icon
                else:
                    if not existing_tx.has_confirmed:
                        icon = f"{self.script_path}/images/confirmed.png"
                        existing_tx.confirmations_icon.image = icon
                        existing_tx.has_confirmed = True


    async def reload_transactions(self):
        self.is_loading = True
        self.transactions_from = 0
        self.no_more_transactions = None
        self.scroll_toggle = None
        self.transactions_data.clear()
        self.transactions_box.clear()
        transactions = self.get_transactions(self.transactions_count, self.transactions_from)
        for data in transactions:
            txid = data[3]
            transaction_info = Txid(self.app, self.main, self.script_path, self.utils, self.units, data)
            self.transactions_data[txid] = transaction_info
            self.transactions_box.add(transaction_info)
            await asyncio.sleep(0.0)
        self.vertical_position = 0
        self.is_loading = None


    def _handle_on_scroll(self, scroll):
        if self.no_more_transactions or self.scroll_toggle:
            return
        if self.vertical_position == self.max_vertical_position:
            self.app.loop.create_task(self.get_transactions_archive())


    async def get_transactions_archive(self):
        if self.scroll_toggle:
            return
        self.scroll_toggle = True
        self.transactions_from += 20
        transactions = self.get_transactions(self.transactions_count, self.transactions_from)
        if not transactions:
            self.no_more_transactions = True
            return
        for data in transactions:
            txid = data[3]
            transaction_info = Txid(self.app, self.main, self.script_path, self.utils, self.units, data)
            self.transactions_data[txid] = transaction_info
            self.transactions_box.add(transaction_info)
            await asyncio.sleep(0.0)
        self.scroll_toggle = None