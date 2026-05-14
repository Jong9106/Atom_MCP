import asyncio
import httpx

BASE_URL = "https://us-central1-atomchat-io.cloudfunctions.net"
CHANNEL_PUBLIC_TOKEN = "1be8ec5c-b3ab-ec0b-f822-a234c9d70f8f"

async def send_template():
    headers = {
        "Authorization": f"Bearer {CHANNEL_PUBLIC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "phoneNumber": "573103232870",
        "templateId": "tVEmzzycCyPwW0f1Ufkx",
        "params": {
            "first_name": "Cliente"
        }
    }
    
    print(f"Enviando plantilla 'tVEmzzycCyPwW0f1Ufkx' a 573103232870...")
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}/templates/"
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_template())
