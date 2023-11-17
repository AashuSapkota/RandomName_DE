from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import boto3
from botocore.exceptions import ClientError
from io import BytesIO


logging.basicConfig(
    filename='kafka_consumer_s3.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

class KafkaConsumerApp:
    def __init__(self, kafka_server, topic_name):
        self.consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_server, auto_offset_reset='earliest')
        self.s3_Client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION'),
            endpoint_url=os.getenv('AWS_URL')
        )

    def process_messages(self, message):
        message_value = message.value.decode('utf-8')
        data = json.loads(message_value)
        json_data = json.dumps(data).encode('utf-8')

        user_id = data['username']
        

        try:
            object_name = f"user_{user_id}_{datetime.now().strftime('%Y%m%d%h%M%S')}.json"
            self.upload_file(json_data, os.getenv('S3_BUCKET_NAME'), object_name)
        except Exception as e:
            logging.error(e)

    def upload_file(self, data, bucket, object_name):
        try:
            self.s3_Client.upload_fileobj(BytesIO(data), bucket, object_name)
            logging.info(f"Data uploaded to S3 bucket '{bucket}' as '{object_name}'")
        except ClientError as e:
            logging.error(f"Error uploading data to S3 bucket '{bucket}': {e}")
            return False
        return True

    def consume_messages(self):
        for message in self.consumer:
            try:
                self.process_messages(message)
                logging.info("Message processed successfully!")
            except Exception as e:
                logging.error(f"Error processing message: {e}")


if __name__ == '__main__':
    consumer_app = KafkaConsumerApp(
        os.getenv('KAFKA_SERVER'),
        os.getenv('TOPIC_NAME'),
    )
    consumer_app.consume_messages()