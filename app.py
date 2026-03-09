from flask import Flask, render_template, request, jsonify
from agent import chat

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_route():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        print(f"Message from IP: {ip}")
        user_input = request.json.get("message", "")
        if not user_input.strip():
            return jsonify({"reply": ""})
        reply = chat(user_input)
        if not reply:
            return jsonify({"reply": "sorry, something went wrong, try again!"})
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {e}")
        error = str(e)
        if "rate_limit_exceeded" in error or "429" in error:
            return jsonify({"reply": "woof! 🐾 looks like we've hit the daily limit! i've talked too much today! come back in a few hours and i'll be ready again!"})
        return jsonify({"reply": "something went wrong, try again!"})

if __name__ == "__main__":
    from pyngrok import ngrok
    public_url = ngrok.connect(5000)
    print(f"\n🐾 Share this link with your friend: {public_url}\n")
    app.run(debug=False)