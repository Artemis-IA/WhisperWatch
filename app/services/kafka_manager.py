# app/services/kafka_manager.py
from kafka import KafkaProducer, KafkaConsumer

class KafkaManager:
    def __init__(self, topic_name):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        self.consumer = KafkaConsumer(topic_name, bootstrap_servers=['localhost:9092'])

    def send_message(self, topic, message):
        self.producer.send(topic, message.encode('utf-8'))
        self.producer.flush()

    def consume_messages(self):
        for message in self.consumer:
            print(f"Received message: {message.value.decode('utf-8')}")
