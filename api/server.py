# sse_server.py

from flask import Flask, Response, request, stream_with_context
from threading import Lock
from queue import Queue, Empty
import time

app = Flask(__name__)
user_streams = {}
stream_lock = Lock()

# Event stream generator for each user
def event_stream(user_id):
    q = Queue()
    with stream_lock:
        user_streams[user_id] = q
    try:
        while True:
            try:
                data = q.get(timeout=15)  # Timeout to keep connection alive
                yield f"data: {data}\n\n"
            except Empty:
                # Heartbeat to keep the connection open
                yield f": keep-alive\n\n"
    except GeneratorExit:
        with stream_lock:
            user_streams.pop(user_id, None)

@app.route('/events')
def sse():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Missing user_id", 400
    return Response(stream_with_context(event_stream(user_id)), content_type="text/event-stream")

@app.route('/send/<user_id>', methods=["POST"])
def send_event(user_id):
    data = request.json.get("message", f"Default message for {user_id}")
    with stream_lock:
        if user_id in user_streams:
            user_streams[user_id].put(data)
            return f"Sent message to {user_id}", 200
        else:
            return f"No active stream for {user_id}", 404

if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
