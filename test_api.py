import asyncio
import httpx
import os

BASE_URL = "https://us-central1-atomchat-io.cloudfunctions.net"
COMPANY_TOKEN = "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57"

async def test():
    headers = {
        "Authorization": f"Bearer {COMPANY_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {"phone": "573103232870", "page": 1, "size": 1}
    url = f"{BASE_URL}/clients/"
    print(f"Testing URL: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
