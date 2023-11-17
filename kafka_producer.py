import requests
import json
import time
from cryptography.fernet import Fernet
from kafka import KafkaProducer
from dotenv import load_dotenv
from datetime import datetime
import os
import logging

load_dotenv()

logging.basicConfig(
    filename='kafka_producer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class KafkaProducerApp:
    def __init__(self, kafka_server, topic_name, key):
        self.producer = KafkaProducer(bootstrap_servers=kafka_server)
        self.topic_name = topic_name
        self.key = key
        self.cipher_suite = Fernet(self.key)


    def encrypt_data(self, data: str) -> str:
        data_bytes = data.encode()
        encrypted_data = self.cipher_suite.encrypt(data_bytes)
        return encrypted_data.decode()
    
    def retrieve_user_data(self, url='https://randomuser.me/api/?results=1') -> dict:
        response = requests.get(url)
        return response.json()["results"][0]
    
    def transform_data(self, data: dict) -> dict:
        return {
            "name": f"{data['name']['first']} {data['name']['last']}",
            "gender": data['gender'],
            "country": data['location']['country'],
            "state": data['location']['state'],
            "city": data['location']['city'],
            "email": self.encrypt_data(data['email']),
            "dob": data['dob'],
            "username": self.encrypt_data(data['login']['username']),
            "password": self.encrypt_data(data['login']['password'])
        }
    
    def publish_to_kafka(self, data: dict):
        self.producer.send(self.topic_name, json.dumps(data).encode())


    def stream_data(self, pause_interval, streaming_duration):
        start_time = datetime.now()
        while(datetime.now() - start_time).total_seconds() < streaming_duration:
            try:
                user_data = self.retrieve_user_data()
                transformed_data = self.transform_data(user_data)
                self.publish_to_kafka(transformed_data)
                logging.info("Data published to Kafka")
                time.sleep(pause_interval)
            except Exception as e:
                logging.error(f"Error streaming data: {e}")

if __name__ == '__main__':
    kafka_procuder_app = KafkaProducerApp(
        os.getenv('KAFKA_SERVER'),
        os.getenv('TOPIC_NAME'),
        os.getenv('KEY')
    )
    kafka_procuder_app.stream_data(
        int(os.getenv('PAUSE_INTERVAL')),
        int(os.getenv('STREAMING_DURATION'))
    )
