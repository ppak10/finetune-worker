import websockets
import json
import ssl
import os

from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()

# Function to generate text
def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=50, do_sample=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

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

import asyncio
import threading

from threading import Lock

conversation_thread_running = False
conversation_thread_lock = Lock()

def open_conversation_websocket_thread(conversation_id, content = None):
    global conversation_thread_running

    def thread_target():
        global conversation_thread_running
        try:
            asyncio.run(open_conversation_websocket(conversation_id, content))
        finally:
            with conversation_thread_lock:
                conversation_thread_running = False  # Reset after it finishes

    with conversation_thread_lock:
        if conversation_thread_running:
            print("Conversation WebSocket already running. Skipping.")
            return
        conversation_thread_running = True

    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()

conversation_shutdown_event = asyncio.Event()

def shutdown_conversation_websocket():
    conversation_shutdown_event.set()

import asyncio
import websockets
import ssl
import json
import os

async def open_conversation_websocket(conversation_id, content=None):
    uri = f"wss://{os.environ.get('DJANGO_HOST')}/ws/conversation/{conversation_id}/machine/"
    headers = {"Authorization": f"Worker {os.environ.get('WORKER_TOKEN')}"}

    # Set up SSL context for WebSocket connection
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with websockets.connect(uri, additional_headers=headers, ssl=ssl_context) as websocket:
            print(f"WebSocket for conversation_id: {conversation_id} opened")

            async def respond_to_prompt(content):
                print(f"Responding to prompt: {content}")
                response = generate_response(content)
                message = {"type": "prompt_response", "content": response}
                print(message)
                await websocket.send(json.dumps(message))

            # Initial response if content is attached
            if content is not None:
                await respond_to_prompt(content)
                print('sent message')

            # # Keep-alive task to ensure connection remains open
            # async def keep_alive():
            #     while conversation_thread_running:
            #         try:
            #             if websocket.open:
            #                 await websocket.send(json.dumps({"type": "ping"}))  # Send a ping every 30 seconds
            #             await asyncio.sleep(30)  # Ping every 30 seconds
            #         except Exception as e:
            #             print(f"Error in keep-alive task: {e}")
            #             break

            # # Start the keep-alive task in the background
            # keep_alive_task = asyncio.create_task(keep_alive())

            while not conversation_shutdown_event.is_set():
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)  # 10s timeout for responsiveness
                    data = json.loads(message)

                    # Handle incoming messages
                    print(f"[WebSocket] Received: {data}")

                    if data.get("type") == "close":
                        print("WebSocket conversation instructed to close.")
                        break

                    elif data.get("type") == "prompt_query":
                        content = data.get("content")
                        print(f"Prompt query message received: {content}")
                        await respond_to_prompt(content)

                except asyncio.TimeoutError:
                    print("WebSocket timeout, checking for shutdown...")

                except websockets.exceptions.ConnectionClosed as e:
                    print(f"WebSocket connection closed: {e}")
                    break

            # Close WebSocket after finishing
            await websocket.close()
            print("WebSocket closed gracefully.")

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        with conversation_thread_lock:
            global conversation_thread_running
            conversation_thread_running = False
            print("Cleaned up thread flag.")

        # # Ensure that the keep-alive task is canceled when the conversation is done
        # if keep_alive_task:
        #     keep_alive_task.cancel()
        #     await keep_alive_task  # Wait for the keep-alive task to finish

        print("WebSocket conversation cleanup complete.")

# async def open_conversation_websocket(conversation_id, content = None):
#     uri = f"wss://{os.environ.get('DJANGO_HOST')}/ws/conversation/{conversation_id}/machine/"
#     headers = {"Authorization": f"Worker {os.environ.get('WORKER_TOKEN')}"}

#     # TODO: Change SSL for production
#     ssl_context = ssl.create_default_context()
#     ssl_context.check_hostname = False
#     ssl_context.verify_mode = ssl.CERT_NONE

#     try:
#         async with websockets.connect(uri, additional_headers=headers, ssl=ssl_context) as websocket:
#             print(f"Websocket for conversation_id: {conversation_id} opened")

#             async def respond_to_prompt(content):
#                 print(f"responding to prompt: {content}")
#                 # response = generate_response(content)
#                 message = {"type": "prompt_response", "content": "content"}
#                 await websocket.send(json.dumps(message))

#             # Initial response if content is attached
#             if content is not None:
#                 await respond_to_prompt(content)

#             while not conversation_shutdown_event.is_set():
#                 try:
#                     message = await asyncio.wait_for(websocket.recv(), timeout=10)  # 10s timeout for responsiveness
#                     data = json.loads(message)

#                     # Handle incoming messages
#                     print(f"[WebSocket] Received: {data}")

#                     if data.get("type") == "close":
#                         print("WebSocket conversation instructed to close.")
#                         break

#                     elif data.get("type") == "prompt_query":
#                         content = data.get("content")
#                         print(f"prompt_query message received: {content}")
#                         await respond_to_prompt(content)

#                 except asyncio.TimeoutError:
#                     print("WebSocket timeout, checking for shutdown...")

#             await websocket.close()
#             print("WebSocket closed gracefully.")

#     except Exception as e:
#         print(f"WebSocket error: {e}")

#     finally:
#         with conversation_thread_lock:
#             global conversation_thread_running
#             conversation_thread_running = False
#             print("Cleaned up thread flag.")

