
import asyncio
from datetime import datetime

from toga import (
    App, MainWindow, Box, Label, ScrollContainer, MultilineTextInput
)
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW
from toga.colors import rgb, GRAY, WHITE, YELLOW, RED, GREENYELLOW

from .storage import DeviceStorage



class Mining(Box):
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

        self.mining_toggle = None

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            title_size = 21
            text_size = 15
        elif 800 < x <= 1200:
            title_size = 18
            text_size = 12
        elif 480 < x <= 800:
            title_size = 15
            text_size = 10
        else:
            title_size = 24
            text_size = 18

        self.title_label = Label(
            text="Mining Stats",
            style=Pack(
                color = GRAY,
                background_color = rgb(40,43,48),
                font_weight=BOLD,
                font_size=title_size,
                text_align=CENTER,
                padding = (5,0,5,0)
            )
        )

        self.status_label = Label(
            text="Status :",
            style=Pack(
                color=GRAY,
                background_color=rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                padding = (0,0,0,10)
            )
        )

        self.status_value = Label(
            text="",
            style=Pack(
                background_color=rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1
            )
        )

        self.recent_label = Label(
            text="Updated :",
            style=Pack(
                color=GRAY,
                background_color=rgb(40,43,48),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1
            )
        )

        self.recent_value = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color=rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER,
                flex = 3
            )
        )

        self.status_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                alignment = CENTER,
                padding = (5,0,5,0)
            )
        )

        self.miner_label = Label(
            text="Miner :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.miner_value = Label(
            text="",
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

        self.miner_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
            )
        )

        self.address_value = MultilineTextInput(
            style=Pack(
                color=WHITE,
                font_size=text_size,
                text_align=CENTER,
                background_color=rgb(20,20,20),
                font_weight=BOLD,
                height = 60,
                padding = 3
            )
        )
        self.address_value._impl.native.setFocusable(False)
        self.address_value._impl.native.setCursorVisible(False)
        self.address_value._impl.native.setLongClickable(False)
        self.address_value._impl.native.setTextIsSelectable(False)

        self.address_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(20,20,20),
                height = 70,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.pool_label = Label(
            text="Pool :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.pool_value = Label(
            text="",
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

        self.pool_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.region_label = Label(
            text="Region :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.region_value = Label(
            text="",
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

        self.region_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.worker_label = Label(
            text="Name :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.worker_value = Label(
            text="",
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

        self.worker_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.shares_label = Label(
            text="Shares :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                padding = (15,0,0,10)
            )
        )

        self.shares_value = Label(
            text="0.0",
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

        self.solutions_label = Label(
            text="Solutions :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.solutions_value = Label(
            text="0.0 Sol/s",
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1.5,
                padding = (15,0,0,0)
            )
        )

        self.shares_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.paid_label = Label(
            text="Paid :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.paid_value = Label(
            text="0.00000000",
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

        self.paid_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.balance_label = Label(
            text="Balance :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.balance_value = Label(
            text="0.00000000",
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

        self.balance_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.immature_label = Label(
            text="Immature :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.immature_value = Label(
            text="0.00000000",
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

        self.immature_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.reward_label = Label(
            text="Reward :",
            style=Pack(
                color=YELLOW,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex = 1,
                padding = (15,0,0,0)
            )
        )

        self.reward_value = Label(
            text="0",
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

        self.reward_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                height = 60,
                alignment=CENTER,
                padding = 3
                
            )
        )

        self.stats_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = rgb(30,33,36),
                flex =1
            )
        )

        self.stats_scroll = ScrollContainer(
            horizontal=False,
            vertical=True,
            style=Pack(
                background_color = rgb(30,33,36),
                flex = 1
            )
        )
        self.stats_scroll.content = self.stats_box

        self.add(
            self.title_label,
            self.status_box,
            self.stats_scroll
        )
        self.status_box.add(
            self.status_label,
            self.status_value,
            self.recent_label,
            self.recent_value
        )
        self.stats_box.add(
            self.miner_box,
            self.address_box,
            self.pool_box,
            self.region_box,
            self.worker_box,
            self.shares_box,
            self.paid_box,
            self.balance_box,
            self.immature_box,
            self.reward_box
        )
        self.miner_box.add(
            self.miner_label,
            self.miner_value
        )
        self.address_box.add(
            self.address_value
        )
        self.pool_box.add(
            self.pool_label,
            self.pool_value
        )
        self.region_box.add(
            self.region_label,
            self.region_value
        )
        self.worker_box.add(
            self.worker_label,
            self.worker_value
        )
        self.shares_box.add(
            self.shares_label,
            self.shares_value,
            self.solutions_label,
            self.solutions_value
        )
        self.paid_box.add(
            self.paid_label,
            self.paid_value
        )
        self.balance_box.add(
            self.balance_label,
            self.balance_value
        )
        self.immature_box.add(
            self.immature_label,
            self.immature_value
        )
        self.reward_box.add(
            self.reward_label,
            self.reward_value
        )

    
    def run_mining_task(self):
        if not self.mining_toggle:
            self.mining_toggle = True
            asyncio.create_task(self.update_mining_stats())


    async def update_mining_stats(self):
        while True:
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/mining'
            result = await self.utils.make_request(device_auth[1], device_auth[2], url)
            if not result or "error" in result:
                color = RED
                status = "Off"
            else:
                color = GREENYELLOW
                status = "On"

                now = int(datetime.now().timestamp())
                formatted_time = datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")

                miner = result.get('miner')
                address = result.get('address')
                pool = result.get('pool')
                region = result.get('region')
                worker = result.get('worker')
                shares = result.get('shares')
                balance = result.get('balance')
                immature = result.get('immature')
                paid = result.get('paid')
                solutions = result.get('solutions')
                reward = result.get('reward')

                self.miner_value.text = miner
                self.address_value.value = address
                self.pool_value.text = pool
                self.region_value.text = region
                self.worker_value.text = worker
                self.shares_value.text = f"{shares:.2f}"
                self.solutions_value.text = f"{solutions:.2f} Sol/s"
                self.paid_value.text = self.units.format_balance(paid)
                self.balance_value.text = self.units.format_balance(balance)
                self.immature_value.text = self.units.format_balance(immature)
                self.reward_value.text = f"{int(reward)} / Day"

                self.recent_value.text = formatted_time
            
            self.status_value.style.color = color
            self.status_value.text = status

            await asyncio.sleep(60)