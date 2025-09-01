
import hashlib
import hmac
import json
from datetime import datetime, timezone

from toga import App
from ..framework import Configuration, Point

import aiohttp
from aiohttp.client_exceptions import ClientError, ClientConnectionError, ServerDisconnectedError
from aiohttp_socks import ProxyConnector, ProxyConnectionError, ProxyError



class Utils:
    def __init__(self, app:App, activity):

        self.app = app
        self.activity = activity


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
    

    async def make_request(self, key, secret, url, params = None):
        if params is None:
            params = {}
        connector = ProxyConnector.from_url(f'socks5://127.0.0.1:9050')
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"{timestamp}.{json.dumps(params, separators=(',', ':'), sort_keys=True)}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha512
        ).hexdigest()
        headers = {
            'Authorization': key,
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    await session.close()
                    return data
        except (ProxyConnectionError, ProxyError, ClientError, ClientConnectionError):
            return None
        except Exception as e:
            print(e)
            return None