import csv
from kafka import KafkaProducer
import json
import time

# Configuration du producteur Kafka
KAFKA_BROKER = 'localhost:9094'  
TOPIC_NAME = 'tweet_topic' 

# Initialiser le producteur Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


def send_csv_to_kafka(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            producer.send(TOPIC_NAME, value=row)
            time.sleep(3)


csv_file_path = '../DATA/simulation.csv'


try:
    send_csv_to_kafka(csv_file_path)
finally:
    producer.close()
