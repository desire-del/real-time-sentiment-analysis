from textblob import TextBlob
from kafka import KafkaConsumer, KafkaProducer
import json

# Configuration Kafka
KAFKA_BROKER = 'localhost:9094'
INPUT_TOPIC = 'tweet_topic'
OUTPUT_TOPIC = 'sentiment_topic'

# Initialisation Kafka
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def analyze_sentiment(tweet):
    """Analyse le sentiment d'un tweet."""
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"

print("✅ Sentiment Analysis Service Started")

for msg in consumer:
    tweet = msg.value.get("text", "")
    sentiment = analyze_sentiment(tweet)
    
    # Créer un message avec le sentiment
    enriched_tweet = {
        "text": tweet,
        "sentiment": sentiment
    }
    
    # Envoyer les données enrichies à un nouveau topic Kafka
    producer.send(OUTPUT_TOPIC, value=enriched_tweet)
    print(f"🔹 Processed: {tweet} → Sentiment: {sentiment}")

