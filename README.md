BTCZWallet-android
==========

**BTCZWallet-android** is a lightweight **mobile client** for
[BTCZWallet-win](<https://github.com/SpaceZ-Projects/BTCZWallet-win>).  
It connects to the server via **HTTPS over Orbot (Tor proxy)** to provide a secure
and private way of managing **BitcoinZ (BTCZ)** on Android devices.

Privacy & Security
------------------

- All communication is routed through **Tor** (via Orbot).  
- The Android client never talks to the server directly.  
- Only your server (BTCZWallet-win) holds and secures wallet data.


Development
-----------

## 🛠 Requirements
- [Python 3.10 or higher](https://www.python.org/downloads/)

Clone the repo

    git clone https://github.com/yourusername/BTCZWallet-android.git
    cd BTCZWallet-android

Create a virtual environment and install dependencies

    python -m venv env
    source env/bin/activate
    python -m pip install --upgrade pip
    pip install briefcase

Build the Android APK

    briefcase create android
    briefcase build android


Setup Android Device (Developer Mode)
-------------------------------------

To install and run the app directly from Briefcase, you need to enable **Developer Mode** 
and **USB debugging** on your Android device.

1. Open **Settings** on your Android device.  
2. Scroll down to **About phone** (or **About device**).  
3. Find **Build number**.  
4. Tap **Build number** 7 times quickly.  
   - You will see a message: *"You are now a developer!"*  
5. Go back to **Settings** → **System** → **Developer options** (this may be in different places depending on your device).  
6. Enable **USB debugging**.  
7. (Optional) Enable **Install via USB** if your device requires it.  
8. Connect your device to your computer with a USB cable.  
9. Confirm the **Allow USB debugging** prompt on your device.  

Running on a Device
-------------------

Once your device is ready and connected, you can install and run the app with::

    briefcase run android

- Briefcase will detect available devices through **adb**.  
- If more than one device/emulator is connected, you will be prompted to select the target device by name.  
- After selection, Briefcase will install the APK and launch the app automatically.  

You can also verify that your device is connected with::

    adb devices

This should list your device ID before running the app.
