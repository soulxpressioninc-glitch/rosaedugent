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
        query = req.get("queryResult", {}).get("queryText", "").lower()
        results = list(teachers.find({}, {"_id": 0}))
        struggling = [t for t in results if t.get("improvement_plan_active") == True]
        if "literacy" in query:
            filtered = [t for t in struggling if t["scores"].get("literacy_instruction", 100) < 60]
        elif "discipline" in query or "classroom" in query:
            filtered = [t for t in struggling if t["scores"].get("classroom_management", 100) < 60]
        elif "lesson" in query or "delivery" in query:
            filtered = [t for t in struggling if t["scores"].get("lesson_delivery", 100) < 60]
        else:
            filtered = struggling
        if not filtered:
            response_text = "All teachers are currently performing well. No active improvement plans at this time."
        else:
            names = ", ".join([t["name"] for t in filtered])
            response_text = f"The following teachers need support: {names}. I recommend immediate coaching sessions, peer observation, and structured improvement plans targeting their weakest areas."
        client.close()
    except Exception as e:
        response_text = f"Database error: {str(e)}"
    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
