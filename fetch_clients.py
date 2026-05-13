import httpx
import json
import asyncio

BASE_URL = "https://us-central1-atomchat-qa.cloudfunctions.net"
COMPANY_TOKEN = "0a4c2c5a-c743-a7d8-bda3-e4d2be863e7b"

headers = {
    "Authorization": f"Bearer {COMPANY_TOKEN}",
    "Content-Type": "application/json"
}

async def get_clients():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/clients/", headers=headers, params={"size": 10, "page": 1})
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code} - {response.text}"

if __name__ == "__main__":
    result = asyncio.run(get_clients())
    print(json.dumps(result, indent=2))
