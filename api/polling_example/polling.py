import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to poll the server
async def poll_for_jobs(url, session):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Received response: {data}")

                # Check if there's a job to do
                if data.get("new_job", False):
                    logger.info("New job detected! Performing job...")
                    # Add your job execution logic here
                    await asyncio.sleep(2)  # simulate job processing
                    logger.info("Job done.")
                else:
                    logger.info("No new job found.")
            else:
                logger.warning(f"Received status code: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"Polling failed: {e}")

# Loop to run polling every 5 seconds
async def start_polling_loop(url, interval=5):
    async with aiohttp.ClientSession() as session:
        while True:
            await poll_for_jobs(url, session)
            await asyncio.sleep(interval)

if __name__ == "__main__":
    polling_url = "http://127.0.0.1:5000/"
    asyncio.run(start_polling_loop(polling_url, interval=5))
