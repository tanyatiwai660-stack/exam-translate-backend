import os
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)
translator = GoogleTranslator(source="en", target="hi")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify(result="")

    return jsonify(result=translator.translate(text))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
