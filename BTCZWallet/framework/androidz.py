
from java import dynamic_proxy, cast
from android.content import ClipboardManager, ClipData
from android.content.res import Configuration
from android.graphics import Point
from android.widget import Toast
from org.beeware.android import MainActivity, IPythonApp

from toga import App


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