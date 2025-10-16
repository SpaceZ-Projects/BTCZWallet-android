BTCZWallet-android
==========

**BTCZWallet-android** is a lightweight **mobile client** for
[BTCZWallet-win](https://github.com/SpaceZ-Projects/BTCZWallet-win).  
It connects to your personal wallet server through an **HTTP channel routed via Tor**,  
with all request data **end-to-end encrypted using PyNaCl**.  

This layered design ensures that every communication between the Android client and the server  
is protected by both **network anonymity (Tor)** and **cryptographic secrecy (PyNaCl)**,  
providing a highly secure and private way to manage **BitcoinZ (BTCZ)** on Android devices.

Privacy & Security
------------------

- All communication is routed through **Tor**, ensuring that network metadata and connection endpoints
  remain fully obfuscated from third parties and external observers.  

- The Android client **never communicates directly** with any external server.  
  All wallet operations occur through your own **BTCZWallet-win** instance running in a trusted environment.  

- Only your local server (**BTCZWallet-win**) holds and secures wallet data —  
  **private keys never leave the machine or traverse any network, not even as signed raw transactions.**  
  This design completely eliminates exposure of key material, preventing any possibility for
  remote attackers to intercept, reconstruct, or exploit sensitive wallet data.  

- The result is a **zero-trust, zero-leak architecture**, where cryptographic integrity and
  privacy are preserved end-to-end by design.


Development
-----------

## 🛠 Requirements
- [Python 3.10 or higher](https://www.python.org/downloads/)

Clone the repo

    git clone https://github.com/yourusername/BTCZWallet-android.git
    cd BTCZWallet-android

Create a virtual environment:

Linux:

    python3 -m venv env
    source env/bin/activate
    python3 -m pip install --upgrade pip

Windows:

    python -m venv env
    ./env/scripts/activate
    python -m pip install --upgrade pip

Install dependencies:

    pip install briefcase

Build the Android APK:

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
