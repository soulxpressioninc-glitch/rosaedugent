import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client["rosaeduagent"]
        teachers = db["teachers"]
        req = request.get_json()
        query = req.get("queryResult", {}).get("queryText", "").lower()
        results = list(teachers.find({"improvement_plan_active": True}, {"_id": 0}))
        if not results:
            response_text = "All teachers are currently performing well. No active improvement plans at this time."
        else:
            names = ", ".join([t["name"] for t in results])
            response_text = f"The following teachers have active improvement plans: {names}. I recommend immediate coaching sessions, peer observation, and structured support targeting their weakest areas."
        client.close()
    except Exception as e:
        response_text = f"Database error: {str(e)}"
    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
