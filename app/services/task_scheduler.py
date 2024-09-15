# app/services/task_scheduler.py
import schedule
import time
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: v.encode('utf-8'))

def task_scheduler():
    # Send periodic scheduling events
    producer.send('task_schedule', 'trigger_scraping')

schedule.every(1).hours.do(task_scheduler)

while True:
    schedule.run_pending()
    time.sleep(1)
