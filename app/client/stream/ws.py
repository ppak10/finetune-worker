import websockets
import json
import ssl
import os

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

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

async def open_websocket_connection_with_conversation_response(worker_instance_id, worker_token, content):
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

        async def respond_to_prompt(content):
            print(f"responding to prompt: {content}")
            response = generate_response(content)
            message = {"type": "prompt_response", "content": response}
            await websocket.send(json.dumps(message))

        await respond_to_prompt(content)

        while True:
            try:
                message = await websocket.recv()
                print(f"WebSocket message received: {message}")

                data = json.loads(message)
                if data.get("type") == "ping":
                    print(f"Ping received via WebSocket. Sending pong...")
                    await respond_to_ping()
                elif data.get("type") == "prompt_query":
                    content = data.get("content")
                    print(f"prompt_query message received: {content}")
                    await respond_to_prompt(content)
                elif data.get("type") == "prompt_response":
                    content = data.get("content")
                    print(f"prompt_response message received: {content}")
                    # await respond_to_prompt(content)

                else:
                    print(f"Received WebSocket message: {data}")

            except websockets.ConnectionClosed:
                print("WebSocket connection closed. Reconnecting...")
                break
