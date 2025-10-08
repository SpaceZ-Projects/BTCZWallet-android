package org.beeware.android;

import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.ComponentName;
import android.os.IBinder;
import android.util.Log;

import org.torproject.jni.TorService;

public class TorController {

    private static final String TAG = "TorController";
    private Context context;
    private TorService torService;
    private boolean isRunning = false;

    public TorController(Context context) {
        this.context = context.getApplicationContext();
    }

    public void startTor() {
        try {
            Intent intent = new Intent(context, TorService.class);
            context.bindService(intent, new ServiceConnection() {
                @Override
                public void onServiceConnected(ComponentName name, IBinder service) {
                    torService = ((TorService.LocalBinder) service).getService();

                    new Thread(() -> {
                        while (torService.getTorControlConnection() == null) {
                            try {
                                Thread.sleep(500);
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            }
                        }
                        Log.i(TAG, "Tor control connection ready");
                        isRunning = true;
                    }).start();
                }

                @Override
                public void onServiceDisconnected(ComponentName name) {
                    torService = null;
                    isRunning = false;
                }
            }, Context.BIND_AUTO_CREATE);

            Log.i(TAG, "Tor starting...");

        } catch (Exception e) {
            Log.e(TAG, "Error starting Tor", e);
        }
    }

    public void stopTor() {
        try {
            if (torService != null) {
                context.unbindService(new ServiceConnection() {
                    @Override
                    public void onServiceConnected(ComponentName name, IBinder service) { }

                    @Override
                    public void onServiceDisconnected(ComponentName name) { }
                });
                torService = null;
                isRunning = false;
            }
            Log.i(TAG, "Tor stopped");
        } catch (Exception e) {
            Log.e(TAG, "Error stopping Tor", e);
        }
    }

    public boolean isRunning() {
        return isRunning;
    }
}