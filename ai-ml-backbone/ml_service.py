from flask import Flask, request, jsonify
from classify import classify_and_route

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    result = classify_and_route(
        subject=data.get('subject'),
        body=data.get('body', ''),
        language=data.get('language')
    )
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting ML service on port 5001...")
    app.run(port=8088)