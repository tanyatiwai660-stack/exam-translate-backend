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

    try:
        translated = translator.translate(text)
        return jsonify(result=translated)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
