import requests
import json
import threading
import time

def listen_sse(r):
    print("Listening for SSE events...")
    for line in r.iter_lines():
        if line:
            print(f"SSE: {line.decode('utf-8')}")

def test_sse():
    # 1. Handshake
    print("Connecting to SSE...")
    r = requests.get("http://localhost:8000/sse", stream=True)
    
    # Start listener thread
    t = threading.Thread(target=listen_sse, args=(r,), daemon=True)
    t.start()

    session_url = ""
    # Wait for session URL from stream
    # This is a bit tricky with threads, let's just do it sequentially for the first bit
    session_url = ""
    
    # Re-doing the first bit synchronously to get the URL
    # (Simplified for this script)
    
    # Wait for the data line
    time.sleep(2) # Give it some time
    
    # Actually, let's just use the previous logic but keep the connection open
    
def test_sse_v2():
    with requests.get("http://localhost:8000/sse", stream=True) as r:
        session_url = ""
        for line in r.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                print(f"SSE: {decoded}")
                if decoded.startswith("data: "):
                    session_url = f"http://localhost:8000{decoded[6:]}"
                    print(f"Session URL: {session_url}")
                    
                    # Send initialization in another thread or after this
                    def send_reqs():
                        time.sleep(1)
                        print("Sending initialization...")
                        init_msg = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "test-client", "version": "1.0"}
                            }
                        }
                        requests.post(session_url, json=init_msg)
                        
                        time.sleep(1)
                        print("Calling tool...")
                        tool_msg = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": "buscar_contactos",
                                "arguments": {"phone": "573103232870"}
                            }
                        }
                        requests.post(session_url, json=tool_msg)

                    threading.Thread(target=send_reqs).start()
                
                if "result" in decoded or "error" in decoded:
                    print("Found response!")
                    # Keep reading for a bit then exit
                    time.sleep(2)
                    break

if __name__ == "__main__":
    test_sse_v2()
