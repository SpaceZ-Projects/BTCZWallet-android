
import asyncio
import time

from java import dynamic_proxy, cast
from java.lang import Runnable
from java.util import Arrays
from android.view import View
from android.content import ClipboardManager, ClipData
from android.content.res import Configuration
from android.graphics import Point
from androidx.activity.result import ActivityResultCallback
from android.widget import Toast
from org.beeware.android import MainActivity, IPythonApp, PortraitCaptureActivity

from com.journeyapps.barcodescanner import ScanOptions, ScanContract

from toga import App


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


class AppProxy(dynamic_proxy(IPythonApp)):
    def __init__(self):
        super().__init__()

        self._back_callback = None
        self._qr_callback = None

    def onBackPressed(self):
        if self._back_callback:
            try:
                result = self._back_callback()
                if isinstance(result, bool):
                    return result
            except Exception as e:
                print("Back callback error:", e)
        return False
    
    def Restart(self):
        MainActivity.singletonThis.Restart()


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