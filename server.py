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
async def buscar_contactos(phone: Optional[str] = None, page: int = 1, size: int = 10, sort: str = "desc"):
    """Busca contactos en Atomchat por teléfono o paginación. 
    El parámetro sort puede ser 'asc' o 'desc' (por defecto 'desc' para ver los más recientes)."""
    params = {"page": page, "size": size, "sort": sort}
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
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    # Extraemos la aplicación web interna (FastAPI/Starlette) de FastMCP
    asgi_app = None
    if hasattr(mcp, "streamable_http_app"):
        asgi_app = mcp.streamable_http_app()
    elif hasattr(mcp, "get_asgi_app"):
        asgi_app = mcp.get_asgi_app()
    elif hasattr(mcp, "_asgi_app"):
        asgi_app = mcp._asgi_app
    elif hasattr(mcp, "app"):
        asgi_app = mcp.app
        
    if not asgi_app:
        print("Error crítico: No se encontró la aplicación web dentro de FastMCP.")
    else:
        # Levantamos el servidor en 0.0.0.0
        uvicorn.run(asgi_app, host="0.0.0.0", port=port)