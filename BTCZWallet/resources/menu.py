
import asyncio

from toga import App, MainWindow, OptionContainer, OptionItem
from toga.colors import RED, GREENYELLOW
from ..framework import ToastMessage

from .home import Home
from .receive import Receive
from .send import Send
from .storage import WalletStorage, DeviceStorage


class Menu(OptionContainer):
    def __init__(self, app:App, main:MainWindow, script_path, utils):

        self.home_page = Home(app, utils)
        self.home_option = OptionItem(
            text="Home",
            content=self.home_page,
            icon=f"{script_path}/images/wallet.png"
        )
        self.receive_page = Receive(app, utils)
        self.receive_option = OptionItem(
            text="Receive",
            content=self.receive_page,
            icon=f"{script_path}/images/receive.png"
        )
        self.send_page = Send(app, utils)
        self.send_option = OptionItem(
            text="Send",
            content=self.send_page,
            icon=f"{script_path}/images/send.png"
        )
        
        content = [
            self.home_option,
            self.receive_option,
            self.send_option
        ]

        super(Menu, self).__init__(content=content)

        self.app = app
        self.main = main
        self.utils = utils

        self.device_storage = DeviceStorage(self.app)
        self.wallet_storage = WalletStorage(self.app)

        self.server_status = None

        self.app.add_background_task(self.check_network)


    async def check_network(self, widget):
        if await self.utils.is_tor_alive():
            self.app.add_background_task(self.check_addresses)
        else:
            await asyncio.sleep(1)
            self.main.error_dialog(
                title="Tor Network Error",
                message="Failed to connect to the Tor network, ensure Tor is running and accessible"
            )

    async def check_addresses(self, widget):
        async def on_result(widget, result):
            if result is None:
                await asyncio.sleep(1)
                self.app.add_background_task(self.check_addresses)

        wallet = self.wallet_storage.get_addresses()
        if not wallet:
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/addresses'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if not result or "error" in result:
                self.main.error_dialog(
                    title="Connection Failed",
                    message="Failed to connect to the server",
                    on_result=on_result
                )
                return
            transparent = result.get('transparent')
            shielded = result.get('shielded')
            balance = 0.00000000
            self.wallet_storage.insert_addresses(transparent, shielded, balance, balance)
            
        self.run_tasks()


    def run_tasks(self):
        self.app.add_background_task(self.update_server_status)


    async def update_server_status(self, widget):
        while True:
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/status'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if not result or "error" in result:
                self.server_status = None
                status = "Offline"
                color = RED
                ToastMessage("Server is offline, retrying in 30 seconds")
            else:
                self.server_status = True
                status = "Online"
                color = GREENYELLOW
            self.home_page.update_status(status, color)

            await asyncio.sleep(30)