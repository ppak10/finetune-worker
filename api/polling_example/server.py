from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route("/")
def check_for_job():
    # Randomly decide if there's a new job to simulate changing server state
    job_available = random.choice([True, False, False, False])  # ~25% chance
    return jsonify({"new_job": job_available})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
