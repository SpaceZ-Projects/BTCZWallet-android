
import asyncio
import time

from java import dynamic_proxy, cast, jclass
from java.lang import Runnable
from java.util import Arrays
from java.io import FileInputStream
from android.app import AlertDialog
from android.net import Uri
from android.view import View
from android.content import ClipboardManager, ClipData
from android.text import InputType
from android.view.animation import TranslateAnimation
from android.content.res import Configuration
from androidx.documentfile.provider import DocumentFile
from android.graphics import Point, Color
from androidx.activity.result import ActivityResultCallback
from android.widget import Toast, RelativeLayout, LinearLayout, ImageView
from org.beeware.android import MainActivity, IPythonApp, PortraitCaptureActivity

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

        self._back_callback = None
        self._qr_callback = None
        self._config_changed_callback = None

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
            asyncio.create_task(result)


class ToastMessage:
    def __init__(self, message):

        context = App.app.current_window._impl.app.native
        toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
        toast.show()


class CopyText():
    def __init__(
        self,
        text
    ):
        super().__init__()

        self.clipboard_manager = None
        context = App.app.current_window._impl.app.native
        clipboard_service = context.getSystemService(
            context.CLIPBOARD_SERVICE
        )
        self.clipboard_manager = cast(
            ClipboardManager,
            clipboard_service
        )
        clip_data = ClipData.newPlainText("button", text)
        self.clipboard_manager.setPrimaryClip(clip_data)
        ToastMessage("Copied to clipboard")


class RelativeDialog:
    def __init__(self, activity, title=None, cancelable=True, top_space=40, bottom_space=40):
        super().__init__()

        self.activity = activity
        self.dialog = None
        self.top_space = top_space
        self.bottom_space = bottom_space

        builder = AlertDialog.Builder(activity)
        builder.setCancelable(cancelable)

        if title:
            builder.setTitle(title)

        self.layout = RelativeLayout(activity)
        builder.setView(self.layout)

        self.dialog = builder.create()
        self.last_view_id = 0
        self.view_map = {}
        self.view_order = []

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
        self.activity.runOnUiThread(RunnableProxy(self.dialog.show))

    def hide(self):
        if self.dialog and self.dialog.isShowing():
            self.activity.runOnUiThread(RunnableProxy(self.dialog.dismiss))
