import os
import aiohttp
import asyncio

async def listen_for_events(user_id, worker_token):
    url = f"https://host.docker.internal:8000/v1/worker_event/{user_id}/"
    headers = {
        "Authorization": f"Worker {worker_token}"
    }
    
    timeout = aiohttp.ClientTimeout(sock_read=None)  # Disable read timeout
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        try:
            async with session.get(url, ssl=False) as response:
                print(f"Connected as {user_id}, status: {response.status}")
                
                # Check for non-2xx responses and print error details
                if response.status != 200:
                    error_details = await response.text()
                    print(f"[{user_id}] Error details: {error_details}")
                    response.raise_for_status()  # Raise exception for non-2xx responses

                async for line in response.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data:"):
                        message = decoded[5:].strip()
                        print(f"[{user_id}] Received message: {message}")
                    elif decoded.startswith(":"):
                        print(f"[{user_id}] Heartbeat")

        except aiohttp.ClientResponseError as e:
            print(f"[{user_id}] HTTP error occurred: {e.status} - {e.message}")
        except Exception as e:
            print(f"[{user_id}] An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    user = "alice"
    worker_token = os.environ.get("WORKER_TOKEN")
    asyncio.run(listen_for_events(user, worker_token))
