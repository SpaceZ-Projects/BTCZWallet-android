
import asyncio
import time
import json
from collections import deque
import os
from pathlib import Path

from java import dynamic_proxy, cast, jclass
from java.lang import Runnable, Boolean, String
from java.util import Arrays
from java.io import FileInputStream, File
from android.app import AlertDialog, NotificationChannel, NotificationManager, PendingIntent
from android.os import Build, Handler
from android.net import Uri
from android.util import TypedValue, Log
from android.view import View, ViewGroup
from android.view.inputmethod import InputMethodManager
from android.content import ClipboardManager, ClipData, Intent, DialogInterface, Context, ServiceConnection
from android.text import InputType
from android.text.util import Linkify
from android.text.method import LinkMovementMethod
from android.content.res import Configuration, Resources
from androidx.core.app import NotificationCompat, NotificationManagerCompat
from androidx.documentfile.provider import DocumentFile
from android.graphics import Point, Color, BitmapFactory, Paint
from android.graphics.drawable import ColorDrawable, BitmapDrawable
from androidx.activity.result import ActivityResultCallback
from androidx.core.content import FileProvider
from android.widget import Toast, RelativeLayout, LinearLayout, ImageView, ScrollView, PopupMenu
from android.webkit import WebView, WebViewClient, WebChromeClient 

from org.beeware.android import MainActivity, IPythonApp, PortraitCaptureActivity, JSBridge

from org.torproject.jni import TorService

from com.journeyapps.barcodescanner import ScanOptions, ScanContract

from toga import App
from toga.constants import COLUMN, ROW



class RunnableProxy(dynamic_proxy(Runnable)):
    def __init__(self, func):
        super().__init__()
        self.func = func
        
    def run(self):
        self.func()


class QRCallbackProxy(dynamic_proxy(ActivityResultCallback)):
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner

    def onActivityResult(self, result):
        if result and result.getContents():
            contents = result.getContents()
            self.scanner._set_result(contents)
        else:
            self.scanner._set_result(None)


class QRScanner:
    def __init__(self, activity):
        self.activity = activity
        self._launcher = None
        self._future = None
        self._expected_timeout_time = None

        scan_contract = ScanContract()
        callback_proxy = QRCallbackProxy(self)
        self._launcher = self.activity.registerForActivityResult(scan_contract, callback_proxy)

    async def start_scan(self, timeout:int=None):
        self._future = asyncio.get_event_loop().create_future()
        configuration = self.activity.getResources().getConfiguration()

        options = ScanOptions()
        options.setPrompt("Scan a QR Code")
        options.setBeepEnabled(False)
        if configuration.orientation == Configuration.ORIENTATION_PORTRAIT:
            options.setCaptureActivity(PortraitCaptureActivity)
        options.setDesiredBarcodeFormats(Arrays.asList("QR_CODE"))
        if timeout:
            options.setTimeout(timeout * 1000)
            self._expected_timeout_time = time.time() + timeout
        else:
            self._expected_timeout_time = None

        self.activity.runOnUiThread(RunnableProxy(lambda: self._launcher.launch(options)))
        return await self._future

    def _set_result(self, contents):
        if contents is None and self._expected_timeout_time:
            if abs(time.time() - self._expected_timeout_time) < 2:
                contents = "__TIMEOUT__"

        if self._future and not self._future.done():
            self._future.set_result(contents)



class FileShare:
    def __init__(self, activity):
        self.context = activity.getApplicationContext()
        self.package_name = self.context.getPackageName()
        self.fileprovider_authority = f"{self.package_name}.fileprovider"

    def share(self, file_path: str, text=None, mime_type="image/png", chooser_title="Share Qr Code"):
        if not file_path or not os.path.exists(file_path):
            ToastMessage("File does not exist to share")
            return False

        try:
            file = File(file_path)
            uri = FileProvider.getUriForFile(self.context, self.fileprovider_authority, file)

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType(mime_type)
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

            if text:
                intent.putExtra(Intent.EXTRA_TEXT, text)

            chooser = Intent.createChooser(intent, chooser_title)
            chooser.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            self.context.startActivity(chooser)
            return True

        except Exception as e:
            ToastMessage(f"Error sharing file: {e}")
            print("Error sharing file:", e)
            return False



class SelectFolderCallback(dynamic_proxy(ActivityResultCallback)):
    def __init__(self, picker):
        super().__init__()
        self.picker = picker

    def onActivityResult(self, uri):
        if uri:
            self.picker._set_result(uri.toString())
        else:
            self.picker._set_result(None)



class SelectFolderDialog:
    def __init__(self, activity):
        self.activity = activity
        self._future = None

        callback_proxy = SelectFolderCallback(self)
        self._launcher = self.activity.registerForActivityResult(
            jclass("androidx.activity.result.contract.ActivityResultContracts$OpenDocumentTree")(),
            callback_proxy
        )

    async def pick_folder(self):
        self._future = asyncio.get_event_loop().create_future()

        def launch_intent():
            self._launcher.launch(None)

        self.activity.runOnUiThread(RunnableProxy(launch_intent))
        return await self._future

    def _set_result(self, folder_uri):
        if self._future and not self._future.done():
            self._future.set_result(folder_uri)




class AppProxy(dynamic_proxy(IPythonApp)):
    def __init__(self):
        super().__init__()

        self.activity = MainActivity.singletonThis
        self.tor_controller = TorController(self.activity)

        self._back_callback = None
        self._qr_callback = None
        self._config_changed_callback = None
        self._js_callback = None


    def set_js_callback(self, callback):
        self._js_callback = callback

    def handle_js_message(self, message):
        try:
            if not message:
                return
            data = json.loads(message)
            if isinstance(data, str) and data.strip().startswith("{"):
                data = json.loads(data)
            if isinstance(data, dict):
                action = data.get("action")
                if not action:
                    return
                event = {k: v for k, v in data.items() if k != "action"}
                if callable(self._js_callback):
                    self._js_callback(action, **event)
        except Exception as e:
            print(f"[ERROR] Failed to handle JS message: {e}")
        

    def onBackPressed(self):
        if self._back_callback:
            try:
                result = self._back_callback()
                if isinstance(result, bool):
                    return result
            except Exception as e:
                print("Back callback error:", e)
        return False
    
    def onConfigurationChanged(self, newConfig):
        if self._config_changed_callback:
            try:
                self._config_changed_callback(newConfig)
            except Exception as e:
                print("Configuration change callback error:", e)

    def Restart(self):
        MainActivity.singletonThis.Restart()

    def Exit(self):
        MainActivity.singletonThis.Exit()


class FocusChangeListener(dynamic_proxy(View.OnFocusChangeListener)):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def onFocusChange(self, v, hasFocus):
        self._callback(v, bool(hasFocus))


class ClickListener(dynamic_proxy(View.OnClickListener)):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def onClick(self, view):
        result = self.callback(view)
        if asyncio.iscoroutine(result):
            App.app.loop.create_task(result)


class LongClickListener(dynamic_proxy(View.OnLongClickListener)):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def onLongClick(self, v):
        if callable(self.callback):
            self.callback(v)
        return True
    

class MenuClickListener(dynamic_proxy(PopupMenu.OnMenuItemClickListener)):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def onMenuItemClick(self, item):
        title = item.getTitle()
        if hasattr(title, "toString"):
            title = title.toString()
        self.callback(title)
        return True


class Notification:
    CHANNEL_ID = "bitcoinz_wallet"
    CHANNEL_NAME = "BTCZ Notifications"
    MAX_NOTIFICATIONS = 3

    def __init__(self, activity):
        self.activity = activity
        self._notif_counter = 0
        self._active_notifs = deque()
        self._ensure_channel()

    def _ensure_channel(self):
        if Build.VERSION.SDK_INT >= 26:
            channel = NotificationChannel(
                self.CHANNEL_ID,
                self.CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH,
            )
            nm = cast(NotificationManager, self.activity.getSystemService(
                self.activity.NOTIFICATION_SERVICE))
            nm.createNotificationChannel(channel)

    def show(self, title: str, message: str, notif_id: int = 1):
        self._notif_counter += 1
        notif_id = self._notif_counter

        if len(self._active_notifs) >= self.MAX_NOTIFICATIONS:
            oldest_id = self._active_notifs.popleft()
            self.hide(oldest_id)

        self._active_notifs.append(notif_id)

        icon_id = self.activity.getResources().getIdentifier(
            "ic_launcher_round", "mipmap", self.activity.getPackageName()
        )
        builder = NotificationCompat.Builder(self.activity, self.CHANNEL_ID)
        builder.setSmallIcon(icon_id)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setPriority(NotificationCompat.PRIORITY_HIGH)
        builder.setDefaults(NotificationCompat.DEFAULT_ALL)
        builder.setAutoCancel(True)
        intent = Intent(self.activity, self.activity.getClass())
        pending = PendingIntent.getActivity(
            self.activity, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        )
        builder.setFullScreenIntent(pending, True)

        nm = getattr(NotificationManagerCompat, "from")(self.activity)
        nm.notify(notif_id, builder.build())

    def hide(self, notif_id: int):
        nm = getattr(NotificationManagerCompat, "from")(self.activity)
        nm.cancel(notif_id)
        if notif_id in self._active_notifs:
            self._active_notifs.remove(notif_id)


class ToastMessage:
    def __init__(self, message):

        context = App.app.current_window._impl.app.native
        toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
        toast.show()


class CopyText:
    def __init__(self, text):

        clipboard_manager = None
        context = App.app.current_window._impl.app.native
        clipboard_service = context.getSystemService(
            context.CLIPBOARD_SERVICE
        )
        clipboard_manager = cast(
            ClipboardManager,
            clipboard_service
        )
        clip_data = ClipData.newPlainText("button", text)
        clipboard_manager.setPrimaryClip(clip_data)
        ToastMessage("Copied to clipboard")


class OnCancelListener(dynamic_proxy(DialogInterface.OnCancelListener)):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def onCancel(self, dialog):
        if callable(self.callback):
            self.callback()


class RelativeDialog:
    def __init__(self, activity, title=None, cancelable=True, top_space=40, bottom_space=40, view_space=0, scrollable=False, on_cancel=None):

        self.activity = activity
        self.dialog = None
        self.top_space = top_space
        self.bottom_space = bottom_space
        self.view_space = view_space
        self.scrollable = scrollable
        self._on_cancel = on_cancel

        builder = AlertDialog.Builder(activity)
        builder.setCancelable(cancelable)

        if title:
            builder.setTitle(title)

        if scrollable:
            self.scroll = ScrollView(activity)
            self.layout = RelativeLayout(activity)
            self.scroll.addView(self.layout)
            builder.setView(self.scroll)
        else:
            self.layout = RelativeLayout(activity)
            builder.setView(self.layout)

        self.dialog = builder.create()
        self.dialog.setOnCancelListener(
            OnCancelListener(lambda: self._handle_cancel())
        )
        self.last_view_id = 0
        self.view_map = {}
        self.view_order = []

    @property
    def cancelable(self) -> bool:
        return self.dialog.isCancelable()

    @cancelable.setter
    def cancelable(self, value: bool):
        self.dialog.setCancelable(bool(value))

    def _convert_box(self, box):
        direction = getattr(box.style, "direction", COLUMN)
        ll = LinearLayout(self.activity)
        if direction == ROW:
            ll.setOrientation(LinearLayout.HORIZONTAL)
        else:
            ll.setOrientation(LinearLayout.VERTICAL)

        padding = getattr(box.style, "padding", (0, 0, 0, 0))
        if isinstance(padding, tuple):
            ll.setPadding(*padding)
        elif isinstance(padding, int):
            ll.setPadding(padding, padding, padding, padding)

        for child in box.children:
            child_native = child._impl.native
            child_params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT,
            )
            ll.addView(child_native, child_params)

        return ll

    def _parse_size(self, val, default):
        if val is None:
            return default
        if isinstance(val, str):
            try:
                return int(val)
            except Exception:
                return default
        if isinstance(val, (int, float)):
            return int(val)
        return default

    def _make_params(self, view, native_view):
        width = RelativeLayout.LayoutParams.WRAP_CONTENT
        height = RelativeLayout.LayoutParams.WRAP_CONTENT

        if hasattr(view, "style") and getattr(view.style, "flex", 0) > 0:
            width = RelativeLayout.LayoutParams.MATCH_PARENT

        if isinstance(native_view, ImageView) and hasattr(view, "style"):
            sw = getattr(view.style, "width", None)
            sh = getattr(view.style, "height", None)

            width = self._parse_size(sw, width)
            height = self._parse_size(sh, height)
            native_view.setAdjustViewBounds(True)
            native_view.setScaleType(ImageView.ScaleType.FIT_XY)

        params = RelativeLayout.LayoutParams(width, height)
        params.addRule(RelativeLayout.CENTER_HORIZONTAL)
        return params


    def _apply_margins(self):
        count = len(self.view_order)
        for i, toga_view in enumerate(self.view_order):
            native_view = self.view_map[toga_view]
            lp = native_view.getLayoutParams()
            lp.topMargin = 0
            lp.bottomMargin = 0

            if i == 0:
                lp.topMargin = self.top_space
            else:
                lp.topMargin = self.view_space

            if i == count - 1:
                lp.bottomMargin = self.bottom_space

            if isinstance(native_view, ImageView):
                lp.topMargin += 20

            if i > 0:
                prev_native = self.view_map[self.view_order[i - 1]]
                lp.addRule(RelativeLayout.BELOW, prev_native.getId())

            native_view.setLayoutParams(lp)

    def add(self, *views):
        for view in views:
            if hasattr(view, "children") and view.children:
                native_view = self._convert_box(view)
            else:
                native_view = view._impl.native

            self.last_view_id += 1
            native_view.setId(self.last_view_id)

            params = self._make_params(view, native_view)
            native_view.setLayoutParams(params)

            self.layout.addView(native_view)
            self.view_map[view] = native_view
            self.view_order.append(view)

        self._apply_margins()

    def insert(self, index, view):
        if hasattr(view, "children") and view.children:
            native_view = self._convert_box(view)
        else:
            native_view = view._impl.native

        self.last_view_id += 1
        native_view.setId(self.last_view_id)

        params = self._make_params(view, native_view)
        native_view.setLayoutParams(params)

        self.layout.addView(native_view, index)
        self.view_map[view] = native_view
        self.view_order.insert(index, view)

        self._apply_margins()

    def remove(self, *views):
        for view in views:
            native_view = self.view_map.get(view)
            if native_view:
                self.layout.removeView(native_view)
                del self.view_map[view]
                self.view_order.remove(view)

        self._apply_margins()

    def show(self):
        self.dialog.getWindow().setBackgroundDrawable(ColorDrawable(Color.parseColor("#202225")))
        self.activity.runOnUiThread(RunnableProxy(self.dialog.show))

    def hide(self):
        if self.dialog and self.dialog.isShowing():
            self.activity.runOnUiThread(RunnableProxy(self.dialog.dismiss))

    def _handle_cancel(self):
        if self._on_cancel:
            self.activity.runOnUiThread(RunnableProxy(lambda: self._on_cancel()))



class TorController:
    TAG = "TorController"

    def __init__(self, activity):
        self.context = activity.getApplicationContext()
        self.handler = Handler()
        self.torService = None
        self.isRunning = False
        self._connection = None
        self.progress = 0

    def start_tor(self):
        try:
            intent = Intent(self.context, TorService)
            class MyConnection(dynamic_proxy(ServiceConnection)):
                def onServiceConnected(_self, name, service):
                    self.torService = service.getService()

                    def wait_for_connection():
                        try:
                            conn = self.torService.getTorControlConnection()
                            if conn is None:
                                self.handler.postDelayed(RunnableProxy(wait_for_connection), 100)
                                return

                            status = conn.getInfo("status/bootstrap-phase")
                            if status:
                                try:
                                    progress_str = status.split("PROGRESS=")[1].split(" ")[0]
                                    percent = int(progress_str)
                                except Exception:
                                    percent = 0

                                self.progress = percent
                                if percent >= 100:
                                    self.isRunning = True
                                    Log.i(self.TAG, "Tor fully bootstrapped")
                                    return
                            self.handler.postDelayed(RunnableProxy(wait_for_connection), 100)

                        except Exception as e:
                            Log.e(self.TAG, f"Tor progress error: {e}")
                            self.handler.postDelayed(RunnableProxy(wait_for_connection), 100)

                    self.handler.post(RunnableProxy(wait_for_connection))

                def onServiceDisconnected(_self, name):
                    self.torService = None
                    self.isRunning = False
                    Log.i(self.TAG, "Tor service disconnected")

            self._connection = MyConnection()
            self.context.bindService(intent, self._connection, Context.BIND_AUTO_CREATE)
            Log.i(self.TAG, "Tor starting...")

        except Exception as e:
            Log.e(self.TAG, f"Error starting Tor: {e}")

    def stop_tor(self):
        try:
            if self.torService and self._connection:
                self.context.unbindService(self._connection)
                self.torService = None
                self._connection = None
                self.isRunning = False
                self.handler.removeCallbacksAndMessages(None)
            Log.i(self.TAG, "Tor stopped")
        except Exception as e:
            Log.e(self.TAG, f"Error stopping Tor: {e}")



_handler = None

def set_handler(func):
    global _handler
    _handler = func

def on_js_message(message):
    if _handler:
        _handler(message)
    else:
        print("⚠️ No JS handler registered, message:", message)


class AndroidWebView:
    def __init__(self, activity, content: Path, app_proxy: AppProxy, background_color=None):
        self.activity = activity
        self.content = content
        self.app_proxy = app_proxy
        self.background_color = background_color

        self.control = WebView(activity)
        self.control.setVisibility(View.VISIBLE)

        settings = self.control.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setAllowFileAccess(True)
        settings.setAllowFileAccessFromFileURLs(True)
        settings.setAllowUniversalAccessFromFileURLs(True)
        settings.setDomStorageEnabled(True)
        settings.setSupportZoom(False)

        bridge = JSBridge(app_proxy)
        self.control.addJavascriptInterface(bridge, "AndroidBridge")

        params = RelativeLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        self.control.setLayoutParams(params)
        self.control.setWebViewClient(WebViewClient())
        self.control.setWebChromeClient(WebChromeClient())

        if background_color:
            self.control.setBackgroundColor(background_color)

    def attach_to(self, parent_layout: RelativeLayout):
        parent_layout.addView(self.control)
        self._load_content()

    def _load_content(self):
        if self.content.exists():
            url = f"file:///{self.content.as_posix()}"
            self.control.loadUrl(url)
        else:
            print(f"[WARN] HTML file not found: {self.content}")
   
