import csv
import json
import random
from datetime import datetime
from random import randint
from kafka import KafkaProducer
import time
import ast

KAFKA_BROKER = 'localhost:9094'
TOPIC_NAME = 'tweet_topic'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_tweet_from_csv(row):
    user = row['username']
    text = row['text']
    created_at = row['created_at'] if row['created_at'] else str(datetime.now())
    
    public_metrics_str = row['public_metrics']
    try:
        public_metrics = ast.literal_eval(public_metrics_str)
    except (ValueError, SyntaxError):
        public_metrics = {}
    
    followers_count = public_metrics.get('followers_count', randint(100, 5000))
    retweet_count = public_metrics.get('retweet_count', randint(0, 100))
    favorite_count = public_metrics.get('favorite_count', randint(0, 200))
    
    tweet_data = {
        "user": user,
        "tweet": text,
        "created_at": created_at,
        "followers_count": followers_count,
        "retweet_count": retweet_count,
        "favorite_count": favorite_count,
    }
    
    return tweet_data

def process_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tweet = generate_tweet_from_csv(row)
            producer.send(TOPIC_NAME, value=tweet)
            print(f"Tweet envoyé à Kafka : {json.dumps(tweet, indent=4)}")
            time.sleep(3)

csv_file = '../DATA/sim.csv' 
process_csv(csv_file)
