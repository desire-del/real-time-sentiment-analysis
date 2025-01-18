import csv
import json
import random
from datetime import datetime
from random import randint
from kafka import KafkaProducer
import time

# Configuration Kafka
KAFKA_BROKER = 'localhost:9094'
TOPIC_NAME = 'tweet_topic'

# Configuration du producteur Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Fonction pour générer un tweet à partir des données CSV et en ajoutant des valeurs aléatoires
def generate_tweet_from_csv(row):
    # Extraire les données de la ligne CSV
    user = row['user']  
    text = row['text'] 
    created_at = row['date'] if row['date'] else str(datetime.now()) 

    # Créer un dictionnaire de tweet
    tweet_data = {
        "user": user,
        "tweet": text,
        "created_at": created_at,
        "followers_count": randint(100, 5000),  # Nombre aléatoire de followers
        "retweet_count": randint(0, 100),  # Nombre aléatoire de retweets
        "favorite_count": randint(0, 200),  # Nombre aléatoire de likes
    }
    
    return tweet_data

# Lire le fichier CSV et générer les tweets
def process_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tweet = generate_tweet_from_csv(row)
            # Envoi du tweet au topic Kafka
            producer.send(TOPIC_NAME, value=tweet)
            print(f"Tweet envoyé à Kafka : {json.dumps(tweet, indent=4)}")
            time.sleep(3)


csv_file = '../DATA/simulation.csv' 
process_csv(csv_file)
