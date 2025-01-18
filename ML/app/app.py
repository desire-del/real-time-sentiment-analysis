from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Charger le pipeline d'analyse de sentiment
sentiment_pipeline = pipeline("sentiment-analysis")

def get_sentiment(tweet):
    # Utilisation du pipeline Hugging Face pour analyser le sentiment
    result = sentiment_pipeline(tweet)[0]
    score = result['score']
    label = result['label']

    # Appliquer les règles personnalisées
    if label == "POSITIVE" and score > 0.7:
        return "POSITIVE"
    elif label == "NEGATIVE" and score > 0.7:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    try:
        # Récupérer le tweet envoyé dans la requête POST
        data = request.get_json()
        tweet = data.get('tweet', '')

        if not tweet:
            return jsonify({"error": "No tweet provided"}), 400

        # Analyser le sentiment du tweet
        sentiment = get_sentiment(tweet)

        # Retourner la réponse
        return jsonify({"sentiment": sentiment}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
