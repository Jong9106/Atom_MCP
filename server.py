import os
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

# Inicializar FastMCP
mcp = FastMCP("Atomchat_Public_Server")

# Configuración base
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
    params = {}
    if phone != "":
        params["phone"] = phone
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/clients/", headers=get_headers(), params=params)
        return response.json()

@mcp.tool()
async def listar_llamadas(size: str = "10"):
    """Lista las últimas llamadas de la empresa."""
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

@mcp.tool()
async def enviar_plantilla(phone: str, template_name: str, channel_id: str = "", vars: str = ""):
    """Envía una plantilla de WhatsApp. 'vars' debe ser una cadena separada por comas."""
    # Convertimos las variables en una lista si existen
    variables = [v.strip() for v in vars.split(",")] if vars else []
    
    payload = {
        "phone": phone,
        "templateName": template_name,
        "variables": variables
    }
    
    if channel_id:
        payload["channelId"] = channel_id
    
    async with httpx.AsyncClient() as client:
        # Usamos el endpoint estándar de mensajería de Atomchat
        response = await client.post(f"{BASE_URL}/messages/v1/sendTemplate", headers=get_headers(), json=payload)
        return response.json()

# --- Configuración de Transportes (Dual: STDIO + SSE) ---

sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        # Usamos el motor interno oficial de FastMCP
        await mcp.server.run(
            streams[0],
            streams[1],
            mcp.server.create_initialization_options()
        )

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

from starlette.responses import JSONResponse

# Aplicación Starlette para SSE (Render)
app = Starlette(routes=[
    Route("/", endpoint=lambda _: JSONResponse({"status": "ok", "transport": "sse"})),
    Route("/sse", endpoint=handle_sse),
    Route("/messages", endpoint=handle_messages, methods=["POST"])
])

if __name__ == "__main__":
    import uvicorn
    import sys

    # Si se detecta PORT (Render) o el argumento --sse, iniciamos el servidor web
    if os.getenv("PORT") or "--sse" in sys.argv:
        port = int(os.getenv("PORT", 8000))
        print(f"Iniciando servidor SSE en el puerto {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Por defecto, iniciamos en modo STDIO (Local)
        print("Iniciando servidor en modo STDIO (Local)...")
        mcp.run()