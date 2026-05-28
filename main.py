import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb+srv://soulxpressioninc_db_user:Rosa2024@rosaeduagent.3hh4cz3.mongodb.net/?appName=Rosaeduagent"

def get_score(score):
    if isinstance(score, dict):
        return int(score.get("$numberInt", 0))
    return int(score)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client["rosaeduagent"]
        teachers = db["teachers"]
        
        req = request.get_json()
        query = req.get("queryResult", {}).get("queryText", "").lower()
        
        results = list(teachers.find({}, {"_id": 0}))
        
        struggling = [t for t in results if any(
            get_score(score) < 60 for score in t["scores"].values()
        )]
        
        if "literacy" in query:
            filtered = [t for t in struggling if get_score(t["scores"]["literacy_instruction"]) < 60]
        elif "discipline" in query or "classroom" in query:
            filtered = [t for t in struggling if get_score(t["scores"]["classroom_management"]) < 60]
        elif "lesson" in query or "delivery" in query:
            filtered = [t for t in struggling if get_score(t["scores"]["lesson_delivery"]) < 60]
        else:
            filtered = struggling
        
        if not filtered:
            response_text = "All teachers are performing well in that area. No improvement plans needed at this time."
        else:
            names = ", ".join([t["name"] for t in filtered])
            response_text = f"Based on current data, the following teachers need support: {names}. I recommend immediate coaching sessions, peer observation, and a structured improvement plan targeting their lowest scoring areas."
        
        client.close()
        
    except Exception as e:
        response_text = f"Database error: {str(e)}"
    
    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

