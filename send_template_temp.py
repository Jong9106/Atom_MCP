import asyncio
import httpx
import os
import json

BASE_URL = "https://us-central1-atomchat-io.cloudfunctions.net"
COMPANY_TOKEN = "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57"

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
    
    print(f"Sending template...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/messages/v1/sendTemplate", headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_template())
