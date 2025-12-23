
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import json
from datetime import datetime, timezone
import hmac
import hashlib



class StreamClient:
    def __init__(self, units, key, secret, url, on_action):

        self.units = units
        self.key = key
        self.secret = secret
        self.url = url
        self.on_action = on_action
        self.running = False
        self.session = None
        self.connected = asyncio.Event()

    async def connect_once(self):
        params = {}
        params = {k: str(v) for k, v in params.items()}
        message_payload = json.dumps(params, separators=(",", ":"), sort_keys=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"{timestamp}.{message_payload}"
        signature = hmac.new(self.secret.encode(), message.encode(), hashlib.sha512).hexdigest()

        headers = {
            "Authorization": self.key,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
        if not self.session:
            connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
            self.session = aiohttp.ClientSession(connector=connector)
        try:
            async with self.session.get(self.url, headers=headers) as response:
                if response.status != 200:
                    self.connected.clear()
                    print("[SSE] Bad status:", response.status)
                    return
                self.connected.set()
                print("[SSE] Connected")
                async for raw in response.content:
                    if not self.running:
                        break
                    line = raw.decode("utf-8").rstrip("\r\n")
                    if not line:
                        continue
                    if line.startswith("data:"):
                        payload = line[5:].lstrip()
                        await self.on_action(payload)
        except Exception as e:
            print("[SSE] Connection error:", e)
        finally:
            self.connected.clear()
            print("[SSE] Disconnected")
                    

    async def connect(self):
        self.running = True
        while self.running:
            try:
                await self.connect_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print("[SSE] Error:", e)
            if self.running:
                await asyncio.sleep(2)

    async def stop(self):
        self.running = False
        self.connected.clear()
        if self.session:
            await self.session.close()
            self.session = None
        print("[SSE] Stopped")