from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
import logging

logging.basicConfig(
    filename='kafka_consumer_mysql.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

class KafkaConsumerApp:
    def __init__(self, kafka_server, topic_name, db_config):
        self.consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_server, auto_offset_reset='earliest')
        self.db_conn = mysql.connector.connect(**db_config)

    def process_message(self, message):
        message_value = message.value.decode('utf-8')
        data = json.loads(message_value)
        cursor = self.db_conn.cursor()
        dob_date = datetime.strptime(data['dob']['date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')

        insert_query = "INSERT INTO users (name, gender, country, state, city, email, dob_date, dob_age, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (
            data['name'], data['gender'],
            data['country'], data['state'],
            data['city'], data['email'],
            dob_date, data['dob']['age'],
            data['username'], data['password']))
        self.db_conn.commit()

    def consume_messages(self):
        for message in self.consumer:
            try:
                self.process_message(message)
                logging.info("Message processed successfully!")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

if __name__ == '__main__':
    consumer_app = KafkaConsumerApp(
        os.getenv('KAFKA_SERVER'),
        os.getenv('TOPIC_NAME'),
        {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
    )
    consumer_app.consume_messages()