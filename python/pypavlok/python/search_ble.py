import asyncio
from bleak import BleakClient

MAC_ADDRESS = "F9:E0:6C:8F:CC:08"

async def connect():
    async with BleakClient(MAC_ADDRESS) as client:
        print(f"Connected to {MAC_ADDRESS}")
        print(f"Services: {client.services}")

asyncio.run(connect())
