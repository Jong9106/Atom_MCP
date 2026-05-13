import httpx
import json
import asyncio
import os

# Using credentials from server.py which seems to be the "public" one
BASE_URL = "https://us-central1-atomchat-io.cloudfunctions.net"
COMPANY_TOKEN = "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57"

headers = {
    "Authorization": f"Bearer {COMPANY_TOKEN}",
    "Content-Type": "application/json"
}

async def find_agent_by_phone(phone):
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Find the client by phone
        print(f"Searching for client with phone: {phone}...")
        response = await client.get(f"{BASE_URL}/clients/", headers=headers, params={"phone": phone})
        
        if response.status_code != 200:
            return f"Error searching client: {response.status_code} - {response.text}"
        
        data = response.json()
        clients = data.get("clients", [])
        
        if not clients:
            # Maybe the phone format needs adjustment? Or it's just not there.
            return f"No client found with phone {phone} in the main URL."

        client_data = clients[0]
        client_id = client_data.get("id")
        print(f"Client found: {client_data.get('name')} (ID: {client_id})")
        
        # Step 2: Search for conversations or something that links to an agent
        # Looking at the server.py, there isn't a direct tool for conversations.
        # I'll check if there's a conversations endpoint based on common patterns.
        print(f"Checking for conversations for client ID: {client_id}...")
        conv_response = await client.get(f"{BASE_URL}/conversations/", headers=headers, params={"clientId": client_id})
        
        if conv_response.status_code == 200:
            conv_data = conv_response.json()
            return {
                "client": client_data,
                "conversations": conv_data
            }
        else:
            # If conversations endpoint doesn't exist, maybe it's in the client object?
            return {
                "client": client_data,
                "note": "Conversations endpoint returned error or not found",
                "status": conv_response.status_code
            }

if __name__ == "__main__":
    phone = "573103232870"
    result = asyncio.run(find_agent_by_phone(phone))
    print(json.dumps(result, indent=2))
