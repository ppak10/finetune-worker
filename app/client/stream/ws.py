import websockets
import json
import ssl
import os


async def open_websocket_connection(worker_instance_id, worker_token):
    uri = f"wss://{os.environ.get('DJANGO_HOST')}/ws/worker/{worker_instance_id}/machine/"
    headers = {"Authorization": f"Worker {worker_token}"}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(
        uri, additional_headers=headers, ssl=ssl_context
    ) as websocket:
        print(f"WebSocket connection established for {worker_instance_id}")

        async def respond_to_ping():
            pong_message = {"type": "pong", "status": "ok"}
            await websocket.send(json.dumps(pong_message))

        while True:
            try:
                message = await websocket.recv()
                print(f"WebSocket message received: {message}")

                data = json.loads(message)
                if data.get("type") == "ping":
                    print(f"Ping received via WebSocket. Sending pong...")
                    await respond_to_ping()

                else:
                    print(f"Received WebSocket message: {data}")

            except websockets.ConnectionClosed:
                print("WebSocket connection closed. Reconnecting...")
                break
