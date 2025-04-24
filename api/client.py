import os
import aiohttp
import asyncio
import json

async def respond_to_ping(worker_id, worker_token):
    url = f"https://host.docker.internal:8000/v1/worker_event/{worker_id}/ping/"
    headers = {
        "Authorization": f"Worker {worker_token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(url, ssl=False, json={"worker_id": worker_id}) as resp:
                if resp.status != 200:
                    print(resp)
                    print(f"[{worker_id}] Failed to respond to ping. Status: {resp.status}")
        except Exception as e:
            print(f"[{worker_id}] Ping response error: {e}")

async def listen_for_events(worker_id, worker_token):
    url = f"https://host.docker.internal:8000/v1/worker_event/{worker_id}/"
    headers = {
        "Authorization": f"Worker {worker_token}"
    }
    
    timeout = aiohttp.ClientTimeout(sock_read=None)  # Disable read timeout
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        try:
            async with session.get(url, ssl=False) as response:
                print(f"Connected as {worker_id}, status: {response.status}")
                
                # Check for non-2xx responses and print error details
                if response.status != 200:
                    error_details = await response.text()
                    print(f"[{worker_id}] Error details: {error_details}")
                    response.raise_for_status()  # Raise exception for non-2xx responses

                async for line in response.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data:"):
                        message = decoded[5:].strip()
                        try:
                            data = json.loads(message)
                            if data.get("type") == "ping":
                                print(f"[{worker_id}] Ping received. Sending pong...")
                                await respond_to_ping(worker_id, worker_token)
                            else:
                                print(f"[{worker_id}] Received message: {data}")
                        except json.JSONDecodeError:
                            print(f"[{worker_id}] Received non-JSON message: {message}")
                    elif decoded.startswith(":"):
                        print(f"[{worker_id}] Heartbeat")

        except aiohttp.ClientResponseError as e:
            print(f"[{worker_id}] HTTP error occurred: {e.status} - {e.message}")
        except Exception as e:
            print(f"[{worker_id}] An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    worker_id = os.environ.get("WORKER_ID")
    # worker_id = None
    worker_token = os.environ.get("WORKER_TOKEN")
    # worker_token = ""
    asyncio.run(listen_for_events(worker_id, worker_token))
