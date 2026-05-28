import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client["Rosaeduagent"]
        teachers = db["Teachers"]
        req = request.get_json()
        results = list(teachers.find({}, {"_id": 0}))
        total = len(results)
        names = ", ".join([t["name"] for t in results])
        response_text = f"I found {total} teachers: {names}"
        client.close()
    except Exception as e:
        response_text = f"Database error: {str(e)}"
    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
