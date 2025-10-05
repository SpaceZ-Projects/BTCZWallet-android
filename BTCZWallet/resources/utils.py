
import os
import hashlib
import hmac
import json
from datetime import datetime, timezone
import qrcode

from toga import App
from ..framework import Configuration, Point

import aiohttp
from aiohttp.client_exceptions import ClientError, ClientConnectionError, ServerDisconnectedError
from aiohttp_socks import ProxyConnector, ProxyConnectionError, ProxyError



class Utils:
    def __init__(self, app:App, activity, units):

        self.app = app
        self.activity = activity
        self.units = units

        if not os.path.exists(self.app.paths.cache):
            os.makedirs(self.app.paths.cache)


    def screen_size(self):
        for screen in self.app.screens:
            width = screen.size.width
        return width

    def screen_resolution(self):
        configuration = self.activity.getResources().getConfiguration()
        window_manager = self.activity.getWindowManager()
        display = window_manager.getDefaultDisplay()
        size = Point()
        display.getRealSize(size)
        width = size.x
        height = size.y
        if configuration.orientation == Configuration.ORIENTATION_PORTRAIT:
            x = width
        else:
            x = height
        return x
    

    async def is_tor_alive(self):
        try:
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:9050')
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get('http://check.torproject.org', timeout=10) as response:
                    await response.text()
                    return True
        except (ProxyConnectionError, ClientConnectionError, ServerDisconnectedError) as e:
            return None
        except Exception as e:
            print(e)
            return None
    

    async def make_request(self, key, secret, url, params=None):
        if params is None:
            params = {}
        params = {k: str(v) for k, v in params.items()}

        connector = ProxyConnector.from_url(f'socks5://127.0.0.1:9050')

        message_payload = json.dumps(params, separators=(",", ":"), sort_keys=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"{timestamp}.{message_payload}"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
        encrypted_params = self.units.encrypt_data(secret, json.dumps(params))

        headers = {
            'Authorization': key,
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                if params:
                    async with session.get(url, headers=headers, params={"data": encrypted_params}) as response:
                        data = await response.json()
                        await session.close()
                        return data
                else:
                    async with session.get(url, headers=headers) as response:
                        data = await response.json()
                        await session.close()
                        return data
        except (ProxyConnectionError, ProxyError, ClientError, ClientConnectionError):
            return None
        except Exception as e:
            print(e)
            return None
        

    def qr_generate(self, address):
        qr_filename = f"qr_{address}.png"
        qr_path = os.path.join(self.app.paths.cache, qr_filename)
        if os.path.exists(qr_path):
            return qr_path
        
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=7,
            border=1,
        )
        qr.add_data(address)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        with open(qr_path, 'wb') as f:
            qr_img.save(f)
        
        return qr_path