
import asyncio
import json

from toga import (
    App, MainWindow, OptionContainer, OptionItem, Box
)
from ..framework import ToastMessage
from toga.colors import RED, GREENYELLOW, YELLOW, GRAY

from .home import Home
from .receive import Receive
from .send import Send
from .txs import Transactions
from .book import AddressBook
from .mining import Mining
from .messages import Messages
from .storage import (
    WalletStorage, DeviceStorage, TxsStorage, AddressesStorage,
    MessagesStorage
)


class Menu(OptionContainer):
    def __init__(self, app:App, main:MainWindow, script_path, utils, units):

        self.home_page = Home(app, main, script_path, utils, units)
        self.home_option = OptionItem(
            text="Home",
            content=self.home_page,
            icon=f"{script_path}/images/wallet.png"
        )
        self.receive_page = Receive(app, main, utils)
        self.receive_option = OptionItem(
            text="Receive",
            content=self.receive_page,
            icon=f"{script_path}/images/receive.png"
        )
        self.send_page = Send(app, main, script_path, utils, units)
        self.send_option = OptionItem(
            text="Send",
            content=self.send_page,
            icon=f"{script_path}/images/send.png"
        )
        self.transactions_page = Transactions(app, main, script_path, utils, units)
        self.transactions_option = OptionItem(
            text="Txs",
            content=self.transactions_page,
            icon=f"{script_path}/images/txs.png"
        )
        self.switch_options = Box()
        self.switch_options = OptionItem(
            text="More",
            content=self.switch_options,
            icon=f"{script_path}/images/more.png"
        )
        
        content = [
            self.home_option,
            self.receive_option,
            self.send_option,
            self.transactions_option,
            self.switch_options
        ]

        super(Menu, self).__init__(content=content)

        self.app = app
        self.main = main
        self.script_path = script_path
        self.utils = utils
        self.units = units

        self.device_storage = DeviceStorage(self.app)
        self.wallet_storage = WalletStorage(self.app)
        self.txs_storage = TxsStorage(self.app)
        self.addresses_storage = AddressesStorage(self.app)
        self.messages_storage = MessagesStorage(self.app)

        self.on_select = self.update_current_tab
        self.app.proxy._back_callback = self.on_back_pressed
        self.app.proxy._config_changed_callback = self.on_config_changed

        self.server_status = None
        self.switch_toggle = None
        self.more_toggle = None
        self.read_messages = []
        self.unread_messages = []

        self.book_page = AddressBook(self.app, self.main, self.script_path, self.utils, self.units)
        self.book_option = OptionItem(
            text="Book",
            content=self.book_page,
            icon=f"{script_path}/images/book.png"
        )

        self.mining_page = Mining(self.app, self.main, self, self.script_path, self.utils, self.units)
        self.mining_option = OptionItem(
            text="Mining",
            content=self.mining_page,
            icon=f"{script_path}/images/mining.png"
        )

        self.messages_page = Messages(self.app, self.main, self, self.script_path, self.utils, self.units)
        self.messages_option = OptionItem(
            text="Messages",
            content=self.messages_page,
            icon=f"{script_path}/images/messages.png"
        )

        self.app.loop.create_task(self.check_network())


    async def update_current_tab(self, container):
        await asyncio.sleep(0.1)
        current_tab = self.current_tab.text
        if current_tab == "Home":
            self.home_page.is_active = True
        elif current_tab == "Send":
            self.send_page.is_active = True
            self.send_page.update_toggle()
        elif current_tab == "Txs":
            self.transactions_page.is_active = True
            self.transactions_page.update_toggle()
        elif current_tab == "More":
            self.more_toggle = True
            self.app.loop.create_task(self._on_more_click())
        elif current_tab == "Back":
            self.more_toggle = None
            self.app.loop.create_task(self._on_back_click())
        elif current_tab == "Book":
            self.book_page.is_active = True
            self.book_page.update_toggle()
        elif current_tab == "Mining":
            self.mining_page.is_active = True
            self.mining_page.update_toggle()
        elif current_tab == "Messages":
            self.messages_page.is_active = True
            self.messages_page.update_toggle()

        if current_tab != "Home":
            self.home_page.is_active = None
        if current_tab != "Send":
            self.send_page.is_active = None
        if current_tab != "Txs":
            self.transactions_page.is_active = None
        if current_tab != "Book":
            self.book_page.is_active = None
        if current_tab != "Mining":
            self.mining_page.is_active = None
        if current_tab != "Messages":
            self.messages_page.is_active = None
            if self.messages_page.chat.contacts_toggle:
                self.messages_page.chat.hide_contacts_list()


    async def _on_more_click(self):
        self.switch_toggle = True
        self._impl.native.setClickable(False)
        self._impl.native.setEnabled(False)
        self.content.remove(self.home_option)
        self.current_tab = self.send_option
        self.content.remove(self.receive_option)
        self.current_tab = self.transactions_option
        self.content.remove(self.send_option)
        self.content.append(self.book_option)
        self.current_tab = self.book_option
        self.content.remove(self.transactions_option)
        self.content.append(self.mining_option)
        self.content.append(self.messages_option)
        self.switch_options.icon = f"{self.script_path}/images/back.png"
        self.switch_options.text = "Back"
        self.current_tab = self.book_option
        self._impl.native.setClickable(True)
        self._impl.native.setEnabled(True)
        self.switch_toggle = None

    async def _on_back_click(self):
        self.switch_toggle = True
        self._impl.native.setClickable(False)
        self._impl.native.setEnabled(False)
        self.content.remove(self.messages_option)
        self.content.remove(self.mining_option)
        self.content.remove(self.book_option)
        self.content.append(self.home_option)
        self.current_tab = self.home_option
        self.content.remove(self.switch_options)
        self.content.append(self.receive_option)
        self.content.append(self.send_option)
        self.content.append(self.transactions_option)
        self.switch_options.icon = f"{self.script_path}/images/more.png"
        self.switch_options.text = "More"
        self.content.append(self.switch_options)
        self._impl.native.setClickable(True)
        self._impl.native.setEnabled(True)
        self.switch_toggle = None
        

    def reload_transactions(self):
        if self.transactions_page.transactions_toggle:
            self.transactions_page.transactions_toggle = None
            self.app.loop.create_task(self.transactions_page.reload_transactions())
            

    def on_back_pressed(self):
        def on_result(widget, result):
            if result is True:
                self.app.controller.stop_tor()
                self.app.proxy.Exit()

        if not self.switch_toggle:
            current_tab = self.current_tab.text
            if current_tab == "Home":
                self.main.question_dialog(
                    title="Exit app",
                    message="Are you sure you want exit the app",
                    on_result=on_result
                )
            elif current_tab == "Send" and self.send_page.book_toggle:
                self.send_page.hide_address_book()

            elif current_tab == "Messages" and self.messages_page.chat.contacts_toggle:
                self.messages_page.chat.hide_contacts_list()
            
            elif self.more_toggle:
                self.more_toggle = None
                self.current_tab = self.switch_options
            else:
                self.current_tab = self.home_option
        return True


    async def check_network(self):
        async def on_result(widget, result):
            if result is None:
                await asyncio.sleep(30)
                self.app.loop.create_task(self.check_network())

        self.home_page.update_status("Connecting...", GRAY)
        if await self.utils.is_tor_alive():
            self.app.loop.create_task(self.check_addresses())
            self.app.loop.create_task(self.check_messages_identity())
        else:
            await asyncio.sleep(1)
            self.home_page.update_status("Failed", YELLOW)
            self.main.error_dialog(
                title="Tor Network Error",
                message="Failed to connect to the Tor network, ensure Tor is running and accessible",
                on_result=on_result
            )

    async def check_addresses(self):
        async def on_result(widget, result):
            if result is None:
                await asyncio.sleep(1)
                self.app.loop.create_task(self.check_addresses())

        wallet = self.wallet_storage.get_addresses()
        if not wallet:
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/addresses'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if not result:
                self.main.error_dialog(
                    title="Connection Failed",
                    message="Failed to connect to the server",
                    on_result=on_result
                )
                return
            decrypted = self.units.decrypt_data(device_auth[2], result["data"])
            result = json.loads(decrypted)

            transparent = result.get('transparent')
            shielded = result.get('shielded')
            balance = 0.00000000
            self.wallet_storage.insert_addresses(transparent, shielded, balance, balance)
            self.receive_page.show_qr("transparent")
            
        
    async def check_messages_identity(self):
        async def on_result(widget, result):
            if result is None:
                await asyncio.sleep(1)
                self.app.loop.create_task(self.check_messages_identity())

        identity = self.messages_storage.get_identity()
        if not identity:
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/contacts'
            params = {"get": "identity"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if not result:
                self.main.error_dialog(
                    title="Connection Failed",
                    message="Failed to connect to the server",
                    on_result=on_result
                )
                return
            
            elif result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                address = result.get('address')
                self.messages_storage.insert_identity(address)

        self.messages_page.load_chat()
        self.run_tasks()


    def run_tasks(self):
        self.app.loop.create_task(self.update_server_status())
        self.app.loop.create_task(self.update_balances())
        self.app.loop.create_task(self.update_transactions())
        self.app.loop.create_task(self.update_address_book())
        self.app.loop.create_task(self.update_contacts())


    async def update_server_status(self):
        while True:
            if not self.server_status:
                self.home_page.update_status("Connecting...", GRAY)
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/status'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if not result or "error" in result:
                self.server_status = None
                status = "Offline"
                color = RED
                ToastMessage("Server is offline - retrying in 30 seconds")
            else:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                version = result.get('version')
                min_version = (1, 4, 9)
                if not version:
                    self.main.error_dialog(
                        title="Update Required",
                        message=f"Server version is too old. Please update to at least 1.4.9"
                    )
                    self.server_status = None
                    status = "Offline"
                    color = RED
                else:
                    try:
                        version_tuple = tuple(int(x) for x in version.split("."))
                    except ValueError:
                        self.main.error_dialog(
                            title="Update Required",
                            message=f"Invalid server version format: {version}"
                        )
                        self.server_status = None
                        status = "Offline"
                        color = RED
                    else:
                        if version_tuple < min_version:
                            self.main.error_dialog(
                                title="Update Required",
                                message=f"Server version {version} is too old. Please update to at least 1.4.9"
                            )
                            self.server_status = None
                            status = "Offline"
                            color = RED
                        else:
                            height = result.get('height')
                            currency = result.get('currency')
                            price = result.get('price')
                            self.server_status = True
                            status = "Online"
                            color = GREENYELLOW
                            self.wallet_storage.update_info(height, currency, price)

            self.home_page.update_status(status, color)

            await asyncio.sleep(30)


    async def update_balances(self):
        while True:
            if not self.server_status:
                await asyncio.sleep(1)
                continue
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/balances'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                transparent = result.get('transparent')
                shielded = result.get('shielded')
                self.wallet_storage.update_balances(transparent, shielded)

            await asyncio.sleep(10)


    async def update_transactions(self):
        while True:
            if not self.server_status:
                await asyncio.sleep(1)
                continue
            transactions_data = self.txs_storage.get_transactions(True)
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/transactions'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    tx_type = data.get('type')
                    category = data.get('category')
                    address = data.get('address')
                    txid = data.get('txid')
                    amount = data.get('amount')
                    blocks = data.get('blocks')
                    txfee = data.get('fee')
                    timestamp = data.get('timestamp')
                    if txid not in transactions_data:
                        self.insert_transaction(tx_type, category, address, txid, amount, blocks, txfee, timestamp)
                        if category == "receive":
                            self.app.notify.show(f"Receive", f"{amount} BTCZ")
                    else:
                        self.update_blocks(txid, blocks)

            await asyncio.sleep(15)


    async def update_address_book(self):
        while True:
            if not self.server_status:
                await asyncio.sleep(1)
                continue
            server_addresses = []
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/book'
            params = {"get": "address"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                address_book = self.addresses_storage.get_address_book("address")
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    name = data.get('name')
                    address = data.get('address')
                    server_addresses.append(address)
                    if address not in address_book:
                        self.addresses_storage.insert_book(name, address)

                for address in address_book:
                    if address not in server_addresses:
                        self.addresses_storage.delete_address_book(address)

            await asyncio.sleep(10)


    async def update_contacts(self):
        while True:
            if not self.server_status or not self.messages_storage.get_identity():
                await asyncio.sleep(1)
                continue
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/contacts'
            params = {"get": "contacts"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                server_contacts = []
                contacts = self.messages_storage.get_contacts("contact_id")
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    category = data.get('category')
                    contact_id = data.get('contact_id')
                    username = data.get('username')
                    server_contacts.append(contact_id)
                    if contact_id not in contacts:
                        self.messages_storage.add_contact(category, contact_id, username)

                for id in contacts:
                    if id not in server_contacts:
                        self.messages_storage.delete_contact(id)

            params = {"get": "pending"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                server_pending = []
                pending = self.messages_storage.get_pending("id")
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    category = data.get('category')
                    contact_id = data.get('contact_id')
                    username = data.get('username')
                    server_pending.append(contact_id)
                    if contact_id not in pending:
                        self.messages_storage.add_pending(category, contact_id, username)
                        self.app.notify.show(f"New Request", username)

                for id in pending:
                    if id not in server_pending:
                        self.messages_storage.delete_pending(id)

            await asyncio.sleep(10)


    
    def insert_transaction(self, tx_type, category, address, txid, amount, blocks, txfee, timestamp):
        self.txs_storage.insert_transaction(
            tx_type, category, address, txid, amount, blocks, txfee, timestamp
        )

    def update_blocks(self, txid, blocks):
        self.txs_storage.update_transaction(
            txid, blocks
        )

    def on_config_changed(self, config):
        if config.orientation == 2:
            self.send_page.adjust_size()