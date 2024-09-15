# app/services/kafka_manager.py
from kafka import KafkaProducer, KafkaConsumer
import os

class KafkaManager:
    def __init__(self, topic_name):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.producer = KafkaProducer(bootstrap_servers=[self.bootstrap_servers])
        self.consumer = KafkaConsumer(topic_name, bootstrap_servers=[self.bootstrap_servers])

    def send_message(self, topic, message):
        """Send a message to a Kafka topic."""
        self.producer.send(topic, message.encode('utf-8'))
        self.producer.flush()

    def consume_messages(self):
        """Consume messages from a Kafka topic."""
        for message in self.consumer:
            yield message
