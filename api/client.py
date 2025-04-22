import aiohttp
import asyncio

async def listen_for_events(user_id):
    url = f"http://localhost:5000/events?user_id={user_id}"
    timeout = aiohttp.ClientTimeout(sock_read=None)  # Disable read timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            print(f"Connected as {user_id}, status: {response.status}")
            async for line in response.content:
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data:"):
                    message = decoded[5:].strip()
                    print(f"[{user_id}] Received message: {message}")
                elif decoded.startswith(":"):
                    print(f"[{user_id}] Heartbeat")

if __name__ == "__main__":
    user = "alice"
    asyncio.run(listen_for_events(user))
