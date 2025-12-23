
package org.beeware.android;

import android.webkit.JavascriptInterface;
import com.chaquo.python.PyObject;

public class JSBridge {

    private final PyObject pythonApp;

    public JSBridge(PyObject pythonApp) {
        this.pythonApp = pythonApp;
    }

    @JavascriptInterface
    public void postMessage(String message) {
        if (pythonApp != null) {
            pythonApp.callAttr("handle_js_message", message);
        }
    }
}