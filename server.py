import os
import httpx
import json
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

# Inicializar FastMCP
mcp = FastMCP("Atomchat_Public_Server")

# Configuración base
BASE_URL = os.getenv("ATOMCHAT_BASE_URL", "https://us-central1-atomchat-io.cloudfunctions.net")
COMPANY_TOKEN = os.getenv("ATOMCHAT_COMPANY_TOKEN", "ce79d131-6f9f-175e-a4f6-d6ed0b53bd57")
CHANNEL_PUBLIC_TOKEN = os.getenv("ATOMCHAT_CHANNEL_PUBLIC_TOKEN", "1be8ec5c-b3ab-ec0b-f822-a234c9d70f8f")

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
async def enviar_plantilla(phone: str, template_name: str, vars: str = ""):
    """Envía una plantilla de WhatsApp. 'vars' debe ser un JSON string con las variables (ej: '{"first_name": "Luis"}')."""
    
    payload = {
        "phoneNumber": phone,
        "templateId": template_name,
    }
    
    if vars:
        try:
            payload["params"] = json.loads(vars)
        except Exception:
            pass # Si falla el JSON, se envia sin parametros o se delega el error a la API
        
    # Usamos el token del canal para este endpoint específico
    headers = {
        "Authorization": f"Bearer {CHANNEL_PUBLIC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # Endpoint correcto según la documentación
        response = await client.post(f"{BASE_URL}/templates/", headers=headers, json=payload)
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
    # --- Lógica Dual Inteligente (STDIO o SSE) ---
    
    # Intentamos obtener el puerto. Railway SIEMPRE inyecta 'PORT'.
    port_env = os.getenv("PORT")
    
    # Si hay puerto O se forzó con --sse, corremos el modo Nube (Render/Railway)
    if port_env or "--sse" in sys.argv:
        import uvicorn
        
        # Si no hay port_env pero se usó --sse localmente, usamos 8000 por defecto
        port = int(port_env) if port_env else 8000
        
        print(f"Iniciando servidor web SSE en el puerto {port}...")
        
        sse = SseServerTransport("/messages")

        async def app(scope, receive, send):
            if scope["type"] == "http":
                path = scope["path"]
                
                if path == "/sse":
                    async with sse.connect_sse(scope, receive, send) as streams:
                        internal_server = getattr(mcp, "_mcp_server", getattr(mcp, "_server", getattr(mcp, "server", mcp)))
                        await internal_server.run(
                            streams[0], 
                            streams[1], 
                            internal_server.create_initialization_options()
                        )
                
                elif path == "/messages" and scope["method"] == "POST":
                    await sse.handle_post_message(scope, receive, send)
                
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

        uvicorn.run(app, host="0.0.0.0", port=port)
        
    else:
        # Modo Local (STDIO)
        print("Iniciando servidor en modo STDIO (Local)...")
        mcp.run()