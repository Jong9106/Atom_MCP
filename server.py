import os
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
mcp = FastMCP("Atomchat_Public_Server")

# ... (Aquí mantienes todas tus funciones @mcp.tool que ya escribimos) ...

if __name__ == "__main__":
    # IMPORTANTE: Cambiamos "stdio" por "sse" para que sea una URL pública
    # El puerto 8000 es el estándar para despliegues
    port = int(os.getenv("PORT", 8000))
    mcp.run(transport="sse", port=port)