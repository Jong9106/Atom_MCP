import os
import httpx
# Eliminamos Optional por sugerencia de Antigravity para evitar conflictos en el puente
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
async def buscar_contactos(phone: str = ""):
    """Busca contactos en Atomchat. Para buscar uno especifico, envia el phone."""
    # Eliminamos 'page' y 'size' de aquí porque la API de clientes los rechaza
    params = {}
    if phone != "":
        params["phone"] = phone
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/clients/", headers=get_headers(), params=params)
        return response.json()

@mcp.tool()
async def listar_llamadas(size: str = "10"):
    """Lista las últimas llamadas de la empresa."""
    # Usamos string plano para el parámetro y lo convertimos a entero internamente
    params = {"size": int(size)}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/calls/v1/", headers=get_headers(), params=params)
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
    from mcp.server.sse import SseServerTransport

    port = int(os.getenv("PORT", 8000))
    sse = SseServerTransport("/messages")

    # Enrutador crudo (Raw ASGI): A prueba de balas, sin intermediarios.
    async def app(scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            
            # Ruta GET para abrir el túnel
            if path == "/sse":
                async with sse.connect_sse(scope, receive, send) as streams:
                    # Buscamos el motor interno de FastMCP sin importar su versión
                    internal_server = getattr(mcp, "_mcp_server", getattr(mcp, "_server", getattr(mcp, "server", mcp)))
                    await internal_server.run(
                        streams[0], 
                        streams[1], 
                        internal_server.create_initialization_options()
                    )
            
            # Ruta POST para recibir las peticiones de la IA
            elif path == "/messages" and scope["method"] == "POST":
                await sse.handle_post_message(scope, receive, send)
            
            # Cualquier otra ruta devuelve 404 limpio
            else:
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [(b"content-type", b"text/plain")],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })

    # Levantamos Uvicorn usando nuestra aplicación cruda
    uvicorn.run(app, host="0.0.0.0", port=port)