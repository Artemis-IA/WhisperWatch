import random

import os
from kafka import KafkaProducer
import json

class RLAgent:
    def __init__(self):
        kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_decision(self, decision):
        self.producer.send(os.getenv('KAFKA_TOPIC_SCRAPE_DECISIONS', 'scrape_decisions'), decision)

    def get_decision(self):
        