from flask import Flask, request, Response
from pymongo import MongoClient
import datetime
import os
import openai

app = Flask(__name__)

# MongoDB connection
mongo_uri = "mongodb+srv://hetanshbhuta:PLSWORK@clusterdb.cvr9ahm.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDB"
client = MongoClient(mongo_uri)
db = client.Call_logs  # Capital "C" to match existing DB in Atlas
collection = db.transcripts

# Environment variables
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://your-default-fallback.loca.lt")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>Hi, this is your AI assistant. Please tell me how I can help you.</Say>
        <Record transcribe="true" transcribeCallback="{PUBLIC_URL}/transcribe" maxLength="60" />
    </Response>"""
    return Response(response, mimetype="text/xml")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    print("🔥 /transcribe was called!")

    transcript = request.form.get("TranscriptionText")
    caller = request.form.get("From")
    timestamp = datetime.datetime.utcnow()

    print("📞 Call from:", caller)
    print("📝 Transcript:", transcript)

    # GPT response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly virtual assistant that handles customer service phone calls."},
                {"role": "user", "content": transcript}
            ]
        )
        gpt_reply = response.choices[0].message["content"].strip()
        print("🤖 GPT says:", gpt_reply)
    except Exception as e:
        print("❌ GPT error:", e)
        gpt_reply = "[Error generating GPT response]"

    # Save to MongoDB with confirmation
    try:
        result = collection.insert_one({
            "caller": caller,
            "transcript": transcript,
            "gpt_reply": gpt_reply,
            "timestamp": timestamp
        })
        print("✅ MongoDB Inserted ID:", result.inserted_id)
    except Exception as mongo_error:
        print("❌ MongoDB insert error:", mongo_error)

    return Response("OK", status=200)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
