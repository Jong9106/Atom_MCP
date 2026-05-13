import os
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
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
    """Busca contactos en Atomchat."""
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
    """Inicia una llamada de WhatsApp."""
    payload = {"phone": phone, "channelId": channel_id}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/calls/v1/", headers=get_headers(), json=payload)
        return response.json()

if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route
    from mcp.server.sse import SseServerTransport

    port = int(os.getenv("PORT", 8000))
    
    # 1. Definimos el transporte y la ruta exacta donde la IA enviará los parámetros
    sse = SseServerTransport("/messages")

    # 2. Manejamos el apretón de manos inicial (Handshake)
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            # Extraemos el motor real oculto dentro de FastMCP
            internal_server = getattr(mcp, "_mcp_server", getattr(mcp, "server", mcp))
            await internal_server.run(
                streams[0], 
                streams[1], 
                internal_server.create_initialization_options()
            )

    # 3. Manejamos la recepción de las variables que mande Claude/Cursor
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    # 4. Creamos las dos rutas EXACTAS que los agentes de IA necesitan
    app = Starlette(routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"])
    ])

    # 5. Lanzamos el servidor en el puerto correcto de Render
    uvicorn.run(app, host="0.0.0.0", port=port)