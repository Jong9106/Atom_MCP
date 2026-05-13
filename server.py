import os
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP para transporte público (SSE)
mcp = FastMCP("Atomchat_Public_Server")

# Configuración base desde la documentación
BASE_URL = os.getenv("ATOMCHAT_BASE_URL", "https://us-central1-atomchat-io.cloudfunctions.net")
COMPANY_TOKEN = os.getenv("ATOMCHAT_COMPANY_TOKEN", "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57")

def get_headers():
    return {
        "Authorization": f"Bearer {COMPANY_TOKEN}",
        "Content-Type": "application/json"
    }

@mcp.tool()
async def buscar_contactos(phone: Optional[str] = None, page: int = 1, size: int = 10):
    """Busca contactos en Atomchat por teléfono o paginación."""
    params = {"page": page, "size": size}
    if phone: params["phone"] = phone
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/clients/", headers=get_headers(), params=params)
        return response.json()

@mcp.tool()
async def listar_llamadas(page: int = 1, size: int = 10):
    """Lista las llamadas de la empresa con paginación."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/calls/v1/", headers=get_headers(), params={"page": page, "size": size})
        return response.json()

@mcp.tool()
async def iniciar_llamada_whatsapp(phone: str, channel_id: str):
    """Inicia una llamada de WhatsApp al número indicado."""
    payload = {"phone": phone, "channelId": channel_id}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/calls/v1/", headers=get_headers(), json=payload)
        return response.json()

if __name__ == "__main__":
    # Configuración ESTRICTA para Render/Railway
    port = int(os.getenv("PORT", 8000))
    # Es obligatorio definir host="0.0.0.0" para que la nube lo detecte
    mcp.run(transport="sse", host="0.0.0.0", port=port)