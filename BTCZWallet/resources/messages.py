
import asyncio
import json
from datetime import datetime

from toga import (
    App, MainWindow, Box, ImageView, Label, ScrollContainer,
    MultilineTextInput, Button, NumberInput, TextInput
)
from ..framework import (
    ClickListener, CopyText, InputType, FocusChangeListener,
    RelativeDialog, LongClickListener, PopupMenu, BitmapFactory,
    BitmapDrawable, Boolean, MenuClickListener, Resources, Paint,
    TypedValue, ToastMessage, Context, Linkify, LinkMovementMethod
)
from toga.style.pack import Pack
from toga.constants import COLUMN, CENTER, BOLD, ROW, RIGHT, LEFT
from toga.colors import rgb, WHITE, BLACK, GRAY, RED, YELLOW, GREENYELLOW, CYAN

from .storage import DeviceStorage, MessagesStorage



class Pending(Box):
    def __init__(self, main:MainWindow, pending_list, script_path, utils, data):
        super().__init__(
            style=Pack(
                direction=ROW
            )
        )

        self.main = main
        self.pending_list = pending_list
        self.script_path = script_path
        self.utils = utils

        self.device_storage = DeviceStorage(self.app)
        self.messages_storage = MessagesStorage(self.app)

        category = data[0]
        self.contact_id = data[1]
        username = data[2]

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 15
        elif 800 < x <= 1200:
            text_size = 12
        elif 480 < x <= 800:
            text_size = 10
        else:
            text_size = 18

        self.category_icon = ImageView(
            image=f"{self.script_path}/images/{category}.png",
            style=Pack(
                width=100,
                height=100
            )
        )

        self.username_label = Label(
            text=username,
            style=Pack(
                color=WHITE,
                font_size=text_size,
                font_weight=BOLD
            )
        )

        self.reject_button = Button(
            text="Reject",
            style=Pack(
                color = WHITE,
                background_color = RED
            )
        )

        self.accept_button = Button(
            text="Accpet",
            style=Pack(
                color = BLACK,
                background_color = GREENYELLOW
            ),
            on_press=self.accept_contact
        )

        self.pending_status = Label(
            text=f"",
            style=Pack(
                color= YELLOW,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.reject_button,
            self.accept_button
        )


    async def accept_contact(self, button):
        self.disbale_buttons()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/contacts'
        params = {"accept": self.contact_id}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.enable_buttons()
        elif result and "error" in result:
            self.pending_status.text = "Failed"
            await asyncio.sleep(1)
            self.enable_buttons()
        else:
            self.messages_storage.delete_pending(self.contact_id)
            self.pending_status.text = "Accepted"
            self.pending_list.cancelable = True


    async def reject_contact(self, button):
        self.disbale_buttons()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/contacts'
        params = {"reject": self.contact_id}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.enable_buttons()
        elif result and "error" in result:
            self.pending_status.text = "Failed"
            await asyncio.sleep(1)
            self.enable_buttons()
        else:
            self.messages_storage.delete_pending(self.contact_id)
            self.pending_status.text = "Rejected"
            self.pending_list.cancelable = True
        
    
    def disbale_buttons(self):
        self.pending_list.cancelable = False
        self.remove(
            self.reject_button,
            self.accept_button
        )
        self.pending_status.text = "Processing..."
        self.add(self.pending_status)


    def enable_buttons(self):
        self.pending_list.cancelable = True
        self.remove(self.pending_status)
        self.add(
            self.reject_button,
            self.accept_button
        )


class PendingList(RelativeDialog):
    def __init__(self, app:App, main:MainWindow, script_path, utils, title="Pending contacts", cancelable=True):
        super().__init__(
            app.activity,
            title,
            cancelable,
            view_space=20,
            scrollable=True,
            on_cancel=self.on_cancel_dialog
        )

        self.app = app
        self.main = main
        self.script_path = script_path
        self.utils = utils

        self.messages_storage = MessagesStorage(self.app)

        self.pending_data = {}
        self.is_active = True
        self.no_pending_toggle = None

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 16
        elif 800 < x <= 1200:
            text_size = 13
        elif 480 < x <= 800:
            text_size = 11
        else:
            text_size = 19

        self.empty_label = Label(
            text="Empty list",
            style=Pack(
                color= WHITE,
                font_weight=BOLD,
                font_size=text_size
            )
        )

        self.app.loop.create_task(self.update_pending_list())


    async def update_pending_list(self):
        while True:
            if not self.is_active:
                return
            current_ids = []
            pending = self.messages_storage.get_pending()
            if not pending:

                if not self.no_pending_toggle:
                    self.add(self.empty_label)
                    self.no_pending_toggle = True

                if self.pending_data:
                    for info in list(self.pending_data.values()):
                        self.remove(info)
                    self.pending_data.clear()
            else:
                if self.no_pending_toggle:
                    self.remove(self.empty_label)
                    self.no_pending_toggle = None
                    
                for data in pending:
                    contact_id = data[1]
                    current_ids.append(contact_id)
                    if contact_id not in self.pending_data:
                        pending_info = Pending(self.main, self, self.script_path, self.utils, data)
                        self.insert(0, pending_info)
                        self.pending_data[contact_id] = pending_info

                for old_id in list(self.pending_data.keys()):
                    if old_id not in current_ids:
                        old_info = self.pending_data.pop(old_id)
                        self.remove(old_info)

            await asyncio.sleep(5)

        
    def on_cancel_dialog(self):
        self.is_active = None



class Message(Box):
    def __init__(self, app:App, script_path, utils, units, data):
        super().__init__(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
                alignment=CENTER,
                padding = (10,5,10,5)
            )
        )

        self.app = app
        self.script_path = script_path
        self.utils = utils

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 13
            message_size = 12
            small_size = 10
        elif 800 < x <= 1200:
            text_size = 12
            message_size = 11
            small_size = 9
        elif 480 < x <= 800:
            text_size = 10
            message_size = 9
            small_size = 7
        else:
            text_size = 18
            message_size = 17
            small_size = 15

        author, message, amount, timestamp = data
        if author == "you":
            color = CYAN
            author = "You"
        else:
            color = rgb(114,137,218)

        message_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        self.author_label = Label(
            text=f"{author} :",
            style=Pack(
                color=color,
                background_color=rgb(30,33,36),
                font_size=text_size,
                font_weight=BOLD,
                text_align=LEFT,
                flex=1.5
            )
        )

        self.gift_label = Label(
            text="",
            style=Pack(
                color=YELLOW,
                background_color=rgb(30,33,36),
                font_size=small_size,
                text_align=CENTER,
                flex=1
            )
        )

        self.timestamp_label = Label(
            text=message_time,
            style=Pack(
                color=GRAY,
                background_color=rgb(30,33,36),
                font_size=small_size,
                text_align=CENTER,
                flex=1
            )
        )

        self.info_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(30,33,36),
                alignment=CENTER,
                padding=(0,0,2,0)
            )
        )

        self.message_label = Label(
            text=message,
            style=Pack(
                color=WHITE,
                background_color=rgb(30,33,36),
                font_size=message_size,
                flex=1
            )
        )
        self.message_label._impl.native.setAutoLinkMask(Linkify.WEB_URLS)
        self.message_label._impl.native.setLinksClickable(True)
        self.message_label._impl.native.setMovementMethod(LinkMovementMethod.getInstance())


        self._impl.native.setClickable(True)
        self._impl.native.setOnLongClickListener(
            LongClickListener(
                lambda view, message=message :self.show_message_popmenu(view, message)
            )
        )

        self.add(
            self.info_box,
            self.message_label
        )
        self.info_box.add(
            self.author_label
        )
        if amount > 0.0001:
            gift = amount - 0.0001
            gift_format = units.format_balance(gift)
            gift = f"🎁 {gift_format}"
            self.gift_label.text = gift
            self.info_box.add(self.gift_label)

        self.info_box.add(self.timestamp_label)

        self._wrap_message(message, message_size)


    def _wrap_message(self, message, font_size_sp):
        screen_width_px = self.utils.screen_resolution() - 300
        metrics = Resources.getSystem().getDisplayMetrics()
        font_size_px = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, font_size_sp, metrics)
        paint = Paint()
        paint.setTextSize(font_size_px)
        words = message.split(" ")
        lines = []
        current_line = ""
        current_width = 0
        for word in words:
            word_width = paint.measureText(word + " ")
            if current_width + word_width <= screen_width_px:
                current_line += word + " "
                current_width += word_width
            else:
                if word_width > screen_width_px:
                    part = ""
                    part_width = 0
                    for char in word:
                        char_width = paint.measureText(char)
                        if part_width + char_width > screen_width_px:
                            if current_line:
                                lines.append(current_line.rstrip())
                                current_line = ""
                            lines.append(part)
                            part = char
                            part_width = char_width
                        else:
                            part += char
                            part_width += char_width
                    if part:
                        if current_line:
                            lines.append(current_line.rstrip())
                            current_line = part + " "
                            current_width = paint.measureText(current_line)
                        else:
                            current_line = part + " "
                            current_width = paint.measureText(current_line)
                else:
                    lines.append(current_line.rstrip())
                    current_line = word + " "
                    current_width = word_width

        if current_line:
            lines.append(current_line.rstrip())

        self.message_label.text = "\n".join(lines)


    def show_message_popmenu(self, view, message):
        popup = PopupMenu(self.app.activity, view)
        context_menu = popup.getMenu()

        copy_message_cmd = context_menu.add("Copy message")
        copy_icon = f"{self.script_path}/images/copy.png"
        copy_bmp = BitmapFactory.decodeFile(copy_icon)
        copy_drawable = BitmapDrawable(self.app.activity.getResources(), copy_bmp)
        copy_message_cmd.setIcon(copy_drawable)

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

        popup.setOnMenuItemClickListener(
            MenuClickListener(
                lambda title, message=message :self.on_popmenu_click(title, message)
            )
        )
        popup.show()


    def on_popmenu_click(self, title, message):
        if title == "Copy message":
            CopyText(message)
        

        
class AddContact(RelativeDialog):
    def __init__(self, app:App, main:MainWindow, script_path, utils, title="Add contact", cancelable=True):
        super().__init__(
            app.activity,
            title,
            cancelable,
            view_space=20,
            scrollable=True
        )

        self.app = app
        self.main = main
        self.script_path = script_path
        self.utils = utils

        self.device_storage = DeviceStorage(self.app)

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 16
        elif 800 < x <= 1200:
            text_size = 13
        elif 480 < x <= 800:
            text_size = 11
        else:
            text_size = 19

        self.address_input = TextInput(
            placeholder="Enter address",
            style=Pack(
                color=WHITE,
                font_size=text_size,
                text_align=CENTER,
                flex=1
            ),
            on_change=self.on_address_change
        )

        self.confirm_button = Button(
            text="Send Request",
            enabled=False,
            style=Pack(
                color=BLACK,
                background_color = GRAY
            ),
            on_press=self.send_request
        )

        self.request_status = Label(
            text=f"",
            style=Pack(
                color= YELLOW,
                font_weight=BOLD,
                font_size = text_size
            )
        )

        self.request_success = ImageView(
            image=f"{self.script_path}/images/confirmed.png",
            style=Pack(
                width = 120,
                height= 120
            )
        )

        self.add(
            self.address_input,
            self.confirm_button
        )


    async def send_request(self, button):
        def on_result(widget, result):
            if result is None:
                self.enable_button()
        self.disable_button()
        address = self.address_input.value.strip()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/contacts'
        params = {"request": address}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.enable_button()
        elif result and "error" in result:
            error_message = result.get('error')
            self.request_status.text = "Failed"
            self.main.error_dialog(
                title="Request Failed",
                message=error_message,
                on_result=on_result
            )
        else:
            self.remove(self.address_input)
            self.request_status.text = "Success"
            self.insert(0, self.request_success)
            await asyncio.sleep(3)
            self.hide()

    
    def disable_button(self):
        self.cancelable = False
        self.address_input.readonly = True
        self.remove(self.confirm_button)
        self.request_status.text = "Processing..."
        self.add(self.request_status)


    def enable_button(self):
        self.cancelable = True
        self.address_input.readonly = False
        self.remove(self.request_status)
        self.add(self.confirm_button)


    def on_address_change(self, input):
        value = self.address_input.value
        if not value:
            enbaled = False
            background_color = GRAY
        else:
            enbaled = True
            background_color = GREENYELLOW
        self.confirm_button.enabled = enbaled
        self.confirm_button.style.background_color = background_color



class Contact(Box):
    def __init__(self, app:App, script_path, utils, data):
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

        self.messages_storage = MessagesStorage(self.app)

        self.category = data[0]
        self.contact_id = data[1]
        self.username = data[2]

        x = utils.screen_resolution()
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


        self.category_icon = ImageView(
            image=f"{script_path}/images/{self.category}.png",
            style=Pack(
                background_color=rgb(20,20,20),
                height = icon_width,
                padding=(15,0,0,5),
                alignment=CENTER 
            )
        )

        self.username_label = Label(
            text=self.username,
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex =1,
                padding = (15,0,0,0)
            )
        )

        self.unread_messages = Label(
            text="",
            style=Pack(
                color=WHITE,
                background_color=RED,
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                padding = (15,5,0,0)
            )
        )

        self.unread_icon = ImageView(
            image=f"{script_path}/images/new_message.png",
            style=Pack(
                background_color=rgb(20,20,20),
                height = icon_width,
                padding=(15,10,0,0),
                alignment=CENTER
            )
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.unread_messages
        )

        self.count_unread_messages()
        

    def count_unread_messages(self):
        unread_messages = self.messages_storage.get_unread_messages(self.contact_id)
        count = len(unread_messages)
        if count > 0:
            self.unread_messages.text = f" {count} "
            self.add(self.unread_icon)




class Chat(Box):
    def __init__(self, app:App, main:MainWindow, messages_page, script_path, utils, units):
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
        self.messages_page = messages_page
        self.script_path = script_path
        self.utils = utils
        self.units = units

        self.device_storage = DeviceStorage(self.app)
        self.messages_storage = MessagesStorage(self.app)

        self.task = None
        self.contacts_toggle = None
        self.selected_contact_toggle = None
        self.contact_id = None
        self.loading_toggle = None
        self.send_toggle = None
        self.scroll_toggle = None
        self.last_message_timestamp = None
        self.unread_toggle = None
        self.messages = []
        self.unread_messages = []

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            text_size = 14
            username_size = 16
            icon_width = 35
        elif 800 < x <= 1200:
            text_size = 11
            username_size = 13
            icon_width = 30
        elif 480 < x <= 800:
            text_size = 9
            username_size = 11
            icon_width = 25
        else:
            text_size = 17
            username_size = 19
            icon_width = 40

        self.new_contact = ImageView(
            image=f"{self.script_path}/images/new_contact.png",
            style=Pack(
                background_color=rgb(20,20,20),
                width=icon_width,
                padding = (10,0,10,10)
            )
        )
        self.new_contact._impl.native.setClickable(True)
        self.new_contact._impl.native.setOnClickListener(ClickListener(self.show_new_contact))

        self.pending_contacts = ImageView(
            image=f"{self.script_path}/images/pending.png",
            style=Pack(
                background_color=rgb(20,20,20),
                width=icon_width,
                padding = (10,0,10,10)
            )
        )
        self.pending_contacts._impl.native.setClickable(True)
        self.pending_contacts._impl.native.setOnClickListener(ClickListener(self.show_pending_list))

        self.copy_address = ImageView(
            image=f"{self.script_path}/images/copy.png",
            style=Pack(
                background_color=rgb(20,20,20),
                width=icon_width,
                padding = (10,0,10,10)
            )
        )
        self.copy_address._impl.native.setClickable(True)
        self.copy_address._impl.native.setOnClickListener(ClickListener(self.copy_messages_address))

        self.balances_value = Label(
            text="0.00000000",
            style=Pack(
                color=rgb(114,137,218),
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                flex = 1,
                text_align=RIGHT
            )
        )

        self.contacts_list = ImageView(
            image=f"{self.script_path}/images/contacts.png",
            style=Pack(
                background_color=rgb(20,20,20),
                width=icon_width,
                padding = 10
            )
        )
        self.contacts_list._impl.native.setClickable(True)
        self.contacts_list._impl.native.setOnClickListener(ClickListener(self.show_contacts_list))

        self.menu_box = Box(
            style=Pack(
                direction = ROW,
                background_color=rgb(20,20,20),
                alignment=CENTER
            )
        )

        self.empty_label = Label(
            "You don't have any contacts yet",
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex=1,
                padding = (5,0,5,0)
            )
        )

        self.contacts_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color=rgb(30,30,30),
                alignment=CENTER,
                flex = 1
            )
        )

        self.contacts_scroll = ScrollContainer(
            vertical=True,
            horizontal=False,
            style=Pack(
                background_color=rgb(30,30,30),
                flex = 3
            )
        )
        self.contacts_scroll.content = self.contacts_box

        self.username_label = Label(
            text="",
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=username_size,
                font_weight=BOLD,
                text_align=CENTER,
                flex =1,
                padding = (5,0,5,0)
            )
        )

        self.contact_info_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                alignment=CENTER
            )
        )
        self.contact_info_box.add(self.username_label)

        self.chat_output = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
                flex = 1
            )
        )

        self.output_scroll = ScrollContainer(
            vertical=True,
            horizontal=False,
            style=Pack(
                background_color=rgb(30,33,36),
                flex = 7
            )
        )

        self.output_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(30,33,36),
                flex = 1
            )
        )
        self.output_scroll.content = self.output_box

        self.message_input = MultilineTextInput(
            placeholder="Write message",
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                font_size=text_size,
                flex = 1,
                padding = (0,0,0,5)
            ),
            on_change=self.update_character_count
        )
        self.message_input._impl.native.setOnFocusChangeListener(FocusChangeListener(self.on_focus_change))

        self.character_count = Label(
            text="0/325",
            style=Pack(
                color=GRAY,
                background_color=rgb(20,20,20),
                font_size=text_size
            ),
        )

        self.fee_input = NumberInput(
            style=Pack(
                color = WHITE,
                background_color = rgb(40,43,48),
                font_size=text_size,
                text_align=CENTER
            )
        )
        self.fee_input._impl.native.setInputType(
            InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL
        )
        self.fee_input._impl.native.setText("0.00020000")
        self.fee_input._impl.native.setOnFocusChangeListener(FocusChangeListener(self.on_focus_change))

        self.send_button = Button(
            text="Send",
            style=Pack(
                color=BLACK,
                background_color=GRAY
            ),
            on_press=self.verify_message
        )

        self.send_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color=rgb(20,20,20),
                alignment=CENTER
            )
        )

        self.input_box = Box(
            style=Pack(
                direction=ROW,
                background_color=rgb(20,20,20),
                alignment=CENTER,
                flex=2
            )
        )

        self.unread_label = Label(
            text="___ Unread Messages ___",
            style=Pack(
                color=RED,
                background_color=rgb(30,33,36),
                font_size=text_size,
                text_align=CENTER,
                flex=1
            )
        )

        self.add(
            self.menu_box,
            self.contact_info_box,
            self.output_scroll,
            self.input_box
        )
        self.menu_box.add(
            self.new_contact,
            self.pending_contacts,
            self.copy_address,
            self.balances_value,
            self.contacts_list
        )
        self.output_box.add(
            self.chat_output
        )
        self.input_box.add(
            self.message_input,
            self.send_box
        )
        self.send_box.add(
            self.character_count,
            self.fee_input,
            self.send_button
        )


    def show_contacts_list(self, view):
        if not self.contacts_toggle:
            self.contacts_toggle = True
            self.hide_keyboard()
            self.remove(
                self.contact_info_box,
                self.input_box
            )
            self.output_scroll.style.flex = 4
            self.insert(1, self.contacts_scroll)
            self.app.loop.create_task(self.load_contacts_list())
        else:
            self.hide_contacts_list()


    def hide_contacts_list(self):
        self.contacts_box.clear()
        self.remove(self.contacts_scroll)
        self.output_scroll.style.flex = 7
        self.insert(1, self.contact_info_box)
        self.add(self.input_box)
        self.contacts_toggle = None


    def hide_keyboard(self):
        v = self.chat_output._impl.native
        if not v.isAttachedToWindow():
            return
        v.clearFocus()
        imm = v.getContext().getSystemService(Context.INPUT_METHOD_SERVICE)
        window_token = v.getWindowToken()
        if window_token is not None:
            imm.hideSoftInputFromWindow(window_token, 0)

    
    async def load_contacts_list(self):
        contacts = self.messages_storage.get_contacts()
        if contacts:
            for data in contacts:
                contact_id = data[1]
                username = data[2]
                contact = Contact(self.app, self.script_path, self.utils, data)
                contact._impl.native.setClickable(True)
                contact._impl.native.setOnClickListener(
                    ClickListener(
                        lambda view, contact_id=contact_id, username=username: self.contact_click(view, contact_id, username)
                    )
                )
                contact._impl.native.setOnLongClickListener(
                    LongClickListener(
                        lambda view, contact_id=contact_id, username=username :self.show_contact_popmenu(view, contact_id, username)
                    )
                )
                self.contacts_box.add(contact)
                await asyncio.sleep(0.0)
        else:
            self.contacts_box.add(self.empty_label)
            

    def show_contact_popmenu(self, view, contact_id, username):
        popup = PopupMenu(self.app.activity, view)
        context_menu = popup.getMenu()

        ban_contact_cmd = context_menu.add("Ban contact")
        ban_icon = f"{self.script_path}/images/ban_contact.png"
        ban_bmp = BitmapFactory.decodeFile(ban_icon)
        ban_drawable = BitmapDrawable(self.app.activity.getResources(), ban_bmp)
        ban_contact_cmd.setIcon(ban_drawable)

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

        popup.setOnMenuItemClickListener(
            MenuClickListener(
                lambda title, contact_id=contact_id, username=username :self.on_popmenu_click(title, contact_id, username)
            )
        )
        popup.show()


    def on_popmenu_click(self, title, contact_id, username):
        if title == "Ban contact":
            def on_result(widget, result):
                if result is True:
                    self.app.loop.create_task(self.ban_contact(contact_id))
            self.main.question_dialog(
            title="Ban Contact",
            message=f"Are you sure you want to ban and delete this contact?\n\n"
                    f"- Username: {username}\n"
                    f"- User ID: {contact_id}\n",
            on_result=on_result
        )
            
    
    async def ban_contact(self, contact_id):
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/contacts'
        params = {"ban": contact_id}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
        elif result and "error" in result:
            error_message = result.get('error')
            self.main.error_dialog(
                title="Failed",
                message=error_message
            )
        else:
            self.messages_storage.delete_contact(contact_id)
            self.hide_contacts_list()
            self.main.info_dialog(
                title="Contact Banned",
                message=f"The contact has been successfully banned and deleted"
            )


    def contact_click(self, view, contact_id, username):
        if self.send_toggle:
            return
        if self.contact_id == contact_id:
            self.hide_contacts_list()
            return
        if self.loading_toggle:
            return
        self.output_scroll.on_scroll = None
        self.contact_id = contact_id
        self.hide_contacts_list()
        self.username_label.text = username
        self.chat_output.clear()
        self.last_message_timestamp = None
        self.selected_contact_toggle = True
        self.loading_toggle = True
        self.app.loop.create_task(self.load_messages())

    
    async def load_messages(self):
        self.messages = self.messages_storage.get_messages(self.contact_id)
        if self.messages:
            messages = sorted(self.messages, key=lambda x: x[3], reverse=True)
            recent_messages = messages[:10]
            self.last_message_timestamp = recent_messages[-1][3]
            for data in recent_messages:
                message = Message(self.app, self.script_path, self.utils, self.units, data)
                self.chat_output.insert(0, message)
                await asyncio.sleep(0.0)
            self.output_scroll.vertical_position = self.output_scroll.max_vertical_position

        self.unread_messages = self.messages_storage.get_unread_messages(self.contact_id)
        if self.unread_messages:
            self.unread_toggle = True
            self.chat_output.add(self.unread_label)
            await asyncio.sleep(0.0)
            self.output_scroll.vertical_position = self.output_scroll.max_vertical_position
            await asyncio.sleep(0.0)
            unread_messages = sorted(self.unread_messages, key=lambda x: x[3], reverse=False)
            for data in unread_messages:
                message = Message(self.app, self.script_path, self.utils, self.units, data)
                self.chat_output.add(message)
                await asyncio.sleep(0.0)
        
        await asyncio.sleep(1)
        self.loading_toggle = None
        self.app.loop.create_task(self.update_current_messages(self.contact_id))
        self.output_scroll.on_scroll = self._handle_on_scroll


    async def update_current_messages(self, contact_id):
        while True:
            if contact_id != self.contact_id:
                return
            messages = self.messages_storage.get_messages(self.contact_id)
            if messages:
                for data in messages:
                    if data not in self.messages:
                        message = Message(self.app, self.script_path, self.utils, self.units, data)
                        self.chat_output.add(message)
                        self.messages.append(data)
                        await asyncio.sleep(0.0)
                        self.output_scroll.vertical_position = self.output_scroll.max_vertical_position

            current_unread_messages = []
            unread_messages = self.messages_storage.get_unread_messages(self.contact_id)
            if unread_messages:
                for data in unread_messages:
                    if data not in self.unread_messages:
                        current_unread_messages.append(data)
                            
                if current_unread_messages:
                    if not self.unread_toggle:
                        self.unread_toggle = True
                        self.chat_output.add(self.unread_label)
                        await asyncio.sleep(0.0)

                    for data in current_unread_messages:
                        message = Message(self.app, self.script_path, self.utils, self.units, data)
                        self.chat_output.add(message)
                        self.unread_messages.append(data)
                        await asyncio.sleep(0.0)

            await asyncio.sleep(4)


    async def clean_unread_messages(self):
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/messages'
        params = {"clean": self.contact_id}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            return
        unread_messages = self.messages_storage.get_unread_messages(self.contact_id)
        if unread_messages:
            for data in unread_messages:
                self.messages.append(data)
            self.messages_storage.delete_unread(self.contact_id)
            
        self.unread_toggle = None
        self.chat_output.remove(self.unread_label)


    def show_new_contact(self, view):
        if self.contacts_toggle:
            self.hide_contacts_list()
        newcontact_dialog = AddContact(self.app, self.main, self.script_path, self.utils)
        newcontact_dialog.show()


    def show_pending_list(self, view):
        if self.contacts_toggle:
            self.hide_contacts_list()
        self.hide_keyboard()
        pending_dialog = PendingList(self.app, self.main, self.script_path, self.utils)
        pending_dialog.show()


    def _handle_on_scroll(self, scroll):
        if self.output_scroll.vertical_position == self.output_scroll.max_vertical_position:
            self.app.loop.create_task(self.clean_unread_messages())

        if not self.scroll_toggle:
            if self.output_scroll.vertical_position <= 0:
                self.scroll_toggle = True
                self.app.loop.create_task(self.load_old_messages())


    async def load_old_messages(self):
        messages = self.messages_storage.get_messages(self.contact_id)
        messages = sorted(messages, key=lambda x: x[3], reverse=True)
        last_loaded_message_timestamp = self.last_message_timestamp
        try:
            last_loaded_index = next(i for i, m in enumerate(messages) if m[3] == last_loaded_message_timestamp)
        except StopIteration:
            return
        older_messages = messages[last_loaded_index + 1 : last_loaded_index + 6]
        if older_messages:
            self.last_message_timestamp = older_messages[-1][3]
            for data in older_messages:
                message = Message(self.app, self.script_path, self.utils, self.units, data)
                self.chat_output.insert(0, message)
                await asyncio.sleep(0.0)
            self.output_scroll.vertical_position = 10
        self.scroll_toggle = None


    def update_character_count(self, input):
        message = self.message_input.value.strip()
        if not message:
            self.send_button.style.background_color = GRAY
        else:
            self.send_button.style.background_color = rgb(114,137,218)

        character_count = len(message)
        if character_count > 325:
            self.character_count.style.color = RED
        elif character_count < 325:
            self.character_count.style.color = GRAY
        elif character_count == 325:
            self.character_count.style.color = YELLOW

        value = f"{character_count} / 325"
        self.character_count.text = value


    async def verify_message(self, button):
        message = self.message_input.value.strip()
        character_count = len(message)
        fee = self.fee_input._impl.native.getText().toString().strip()
        if not message:
            self.main.error_dialog(
                title="Message Required",
                message="Enter a message before sending"
            )
            self.message_input.focus()
            return
        elif not self.selected_contact_toggle:
            self.main.error_dialog(
                title="No Contact Selected",
                message="Select a contact from the list before sending a message"
            )
            return
        elif character_count > 325:
            self.main.error_dialog(
                title="Message Too Long",
                message="Message exceeds the maximum length of 325 characters"
            )
            return
        elif float(fee) < 0.0002:
            self.main.error_dialog(
                title="Fee Too Low",
                message="The minimum fee per message is 0.00020000"
            )
            self.fee_input._impl.native.setText("0.00020000")
            return
        await self.send_message(message, fee)


    async def send_message(self, message, amount):
        self.disable_send_button()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/messages'
        params = {"send": self.contact_id, "message": message, "amount": amount}
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            ToastMessage("No response - check your internet connection")
            self.enable_send_button()
        elif result and "error" in result:
            self.enable_send_button()
            error_message = result.get('error')
            self.main.error_dialog(
                title="Failed",
                message=error_message
            )
        else:
            self.message_input.value = ""
            self.fee_input._impl.native.setText("0.00020000")
            self.enable_send_button()


    def disable_send_button(self):
        self.send_toggle = True
        self.send_button.text = "..."
        self.send_button.enabled = False
        self.message_input.readonly = True

    def enable_send_button(self):
        self.send_button.text = "Send"
        self.send_button.enabled = True
        self.message_input.readonly = False
        self.send_toggle = None
        
          
    def on_focus_change(self, v, has_focus):
        if not has_focus:
            value = self.fee_input._impl.native.getText().toString().strip()
            try:
                fee = float(value)
            except ValueError:
                fee = 0.0
            if not value or fee < 0.0002:
                self.fee_input._impl.native.setText("0.00020000")
        else:
            self.app.loop.create_task(self.scroll_to_bottom())

        
    async def scroll_to_bottom(self):
        await asyncio.sleep(0.5)
        self.output_scroll.vertical_position = self.output_scroll.max_vertical_position


    def copy_messages_address(self, view):
        identity = self.messages_storage.get_identity()
        CopyText(identity)



class Messages(Box):
    def __init__(self, app:App, main:MainWindow, menu, script_path, utils, units):
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
        self.menu = menu
        self.script_path = script_path
        self.utils = utils
        self.units = units

        self.device_storage = DeviceStorage(self.app)
        self.messages_storage = MessagesStorage(self.app)

        self.chat = None
        self.is_active = None
        self.messages_toggle = None

        x = self.utils.screen_resolution()
        if 1200 < x <= 1600:
            self.text_size = 14
            notfound_width = 45
        elif 800 < x <= 1200:
            self.text_size = 11
            notfound_width = 40
        elif 480 < x <= 800:
            self.text_size = 9
            notfound_width = 35
        else:
            self.text_size = 17
            notfound_width = 50


        self.no_identity_label = Label(
            text="No identity found on the server\nCreate a new identity using the desktop app",
            style=Pack(
                color=WHITE,
                background_color=rgb(20,20,20),
                text_align=CENTER,
                font_size=self.text_size,
                padding = (0,10,10,10)
            )
        )

        self.no_messages_icon = ImageView(
            image=f"{self.script_path}/images/no_messages.png",
            style=Pack(
                background_color=rgb(20,20,20),
                alignment=CENTER,
                width=notfound_width,
                padding = (10,0,10,0)
            )
        )

        self.notfound_box = Box(
            style=Pack(
                direction=COLUMN,
                background_color = rgb(20,20,20),
                alignment=CENTER
            )
        )

        self.no_identity_box = Box(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                flex = 1,
                alignment=CENTER
            )
        )
        self.no_identity_box.add(
            self.notfound_box
        )
        self.notfound_box.add(
            self.no_messages_icon,
            self.no_identity_label
        )


    def update_toggle(self):
        if not self.messages_toggle and self.messages_storage.get_identity():
            self.messages_toggle = True
            self.app.loop.create_task(self.sync_messages())


    async def sync_messages(self):
        sync_dialog = RelativeDialog(self.app.activity, title="Sync messages", cancelable=False)
        sync_status = Label(
            text="Progress...",
            style=Pack(
                color=YELLOW,
                font_size=self.text_size,
                font_weight=BOLD
            )
        )
        sync_dialog.add(sync_status)
        sync_dialog.show()
        device_auth = self.device_storage.get_auth()
        url = f'http://{device_auth[0]}/messages'
        params = {"get": "read"}
        sync_status.text = "Loading messages..."
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if not result:
            sync_status.text = "Failed"
            await asyncio.sleep(1)
            sync_dialog.hide()
            return
        elif result and "data" in result:
            total = len(result)
            if total > 0:
                self.read_messages = self.messages_storage.get_messages()
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    contact_id = data.get('id')
                    author = data.get('author')
                    message = data.get('message')
                    amount = data.get('amount')
                    timestamp = data.get('timestamp')
                    if timestamp not in self.read_messages:
                        self.messages_storage.message(contact_id, author, message, amount, timestamp)
        
        params = {"get": "unread"}
        sync_status.text = "Loading unread messages..."
        result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
        if result and "data" in result:
            message_count = 0
            total = len(result)
            if total > 0:
                self.unread_messages = self.messages_storage.get_unread_messages()
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    contact_id = data.get('id')
                    author = data.get('author')
                    message = data.get('message')
                    amount = data.get('amount')
                    timestamp = data.get('timestamp')
                    if timestamp not in self.unread_messages:
                        self.messages_storage.unread_message(contact_id, author, message, amount, timestamp)
                        message_count += 1
                if message_count > 0:
                    self.app.notify.show(f"New Message(s)", f"{message_count} New Message(s)")
                        
        sync_status.text = "Completed"

        await asyncio.sleep(1)
        sync_dialog.hide()

        self.app.loop.create_task(self.update_messages())


    async def update_messages(self):
        while True:
            if not self.menu.server_status:
                await asyncio.sleep(1)
                continue
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/messages'
            params = {"get": "read"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    contact_id = data.get('id')
                    author = data.get('author')
                    message = data.get('message')
                    amount = data.get('amount')
                    timestamp = data.get('timestamp')
                    if timestamp not in self.read_messages:
                        self.messages_storage.message(contact_id, author, message, amount, timestamp)

            params = {"get": "unread"}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                for data in result:
                    contact_id = data.get('id')
                    author = data.get('author')
                    message = data.get('message')
                    amount = data.get('amount')
                    timestamp = data.get('timestamp')
                    if timestamp not in self.unread_messages:
                        if self.chat.contact_id == contact_id:
                            self.messages_storage.message(contact_id, author, message, amount, timestamp)
                            if not self.is_active:
                                self.app.notify.show(f"New Message", f"{author}: {message[:50]}")
                        else:
                            self.messages_storage.unread_message(contact_id, author, message, amount, timestamp)
                            self.app.notify.show(f"New Message", f"{author}: {message[:50]}")

            await asyncio.sleep(10)


    def load_chat(self):
        identity = self.messages_storage.get_identity()
        if not identity:
            self.add(
                self.no_identity_box
            )
            return
        self.chat = Chat(self.app, self.main, self, self.script_path, self.utils, self.units)
        self.add(self.chat)

        self.app.loop.create_task(self.update_balance())
        self.app.loop.create_task(self.update_menu())


    async def update_balance(self):
        while True:
            if not self.is_active or not self.menu.server_status:
                await asyncio.sleep(1)
                continue
            device_auth = self.device_storage.get_auth()
            url = f'http://{device_auth[0]}/balance'
            identity = self.messages_storage.get_identity()
            params = {"address": identity}
            result = await self.utils.make_request(device_auth[1], device_auth[2], url, params)
            if result and "data" in result:
                decrypted = self.units.decrypt_data(device_auth[2], result["data"])
                result = json.loads(decrypted)
                balance = result.get('balance')
                self.chat.balances_value.text = self.units.format_balance(balance)

            await asyncio.sleep(10)


    async def update_menu(self):
        while True:
            if not self.is_active:
                await asyncio.sleep(1)
                continue
            unread_messages = self.messages_storage.get_unread_messages()
            if len(unread_messages) > 0:
                self.chat.contacts_list.image = f"{self.script_path}/images/contacts_u.png"
            else:
                self.chat.contacts_list.image = f"{self.script_path}/images/contacts.png"

            pending = self.messages_storage.get_pending()
            if len(pending) > 0:
                self.chat.pending_contacts.image = f"{self.script_path}/images/pending_n.png"
            else:
                self.chat.pending_contacts.image = f"{self.script_path}/images/pending.png"

            await asyncio.sleep(4)