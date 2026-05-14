import asyncio
import httpx
import os

BASE_URL = os.getenv("ATOMCHAT_BASE_URL", "https://us-central1-atomchat-io.cloudfunctions.net")
COMPANY_TOKEN = os.getenv("ATOMCHAT_COMPANY_TOKEN", "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57")

async def send_template():
    headers = {
        "Authorization": f"Bearer {COMPANY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone": "573103232870",
        "templateName": "dc ind",
        "channelId": "+573217526510",
        "variables": []
    }
    
    print(f"Enviando plantilla 'dc ind' a 573103232870 desde canal +573217526510...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Reusing the endpoint from server.py which is what we defined
            url = f"{BASE_URL}/messages/v1/sendTemplate"
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_template())
