# Data Streaming Pipeline using Apacha Kafka
---
This project revolves around a data streaming pipeline that generates random user data, encrypts sensitive details, publishes it to a Kafka topic, and subsequently consumes and processes the data for storage either in an S3 bucket or in MySQL Database.

## Prerequisite
* Apacha Kafka
* MySQL
* s3

### Apache Kafka
Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.
[Find out more about apache kafka](https://kafka.apache.org/)

#### Setup Apache Kafka
Download the apache kafka setup:
```
wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.12-2.8.0.tgz
```

Extract the contents:
```
tar -xvzf kafka_2.12-2.8.0.tgz
```

Apache Kafka can be started using Zookeeper. Run the following commands in order to start all services:
```
cd kafka_2.12-2.8.0
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

Now to create a topic named users_topic run the following command:

```
bin/kafka-topics.sh --create --topic  users_topic --bootstrap-server
```


### s3
Amazon Simple Storage Service (Amazon S3) is an object storage service offering industry-leading scalability, data availability, security, and performance.
[Find out more about s3](https://aws.amazon.com/s3/)

s3 is a paid service provided by AWS. If you want to replicate the s3 environment in your local environment without any costs, you can follow localstack. I do have used the same for this data streaming pipeline.

LocalStack is a cloud service emulator that runs in a single container on your laptop or in your CI environment. It provides various Aws services on free tier.
[Find out more about localstask](https://localstack.cloud/)

#### Setup Localstack
The quickest way to get started with LocalStack is by using LocalStack CLI. It allows you to start LocalStack from your command line. Please make sure that you have a working docker environment on your machine before moving on.
Localstack can be easily setup using pip:

```
python3 -m pip install --upgrade localstack
```

To verify that the LocalStack CLI was installed correctly, you can check the version in your terminal:

```
localstack --version
```

Start the localstack using the following command:

```
localstack start
```

The AWS Command Line Interface (CLI) is a unified tool for creating and managing AWS services via a command line interface. All CLI commands applicable to services implemented within LocalStack can be executed when operating against LocalStack.
You can install aws by using following command:

```
pip install awscli
```

Configure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION:

```
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"
```

Now lets create the s3 bucket using the following command (by default localstack runs on port 4566):

```
aws s3api create-bucket --bucket users-bucket --endpoint-url http://localhost:4566
```

### If you choose MySQL to store data then execute the SQL command inside mysql terminal (it first creates a new database users_db and then create a table users in that database):
```
CREATE DATABASE users_db;
USE users_db;
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),gender VARCHAR(10),country VARCHAR(255),state VARCHAR(255),city VARCHAR(255),email VARCHAR(255),dob_date DATE,dob_age INT,username VARCHAR(255),password VARCHAR(255));
```

## Let's dive into details
### kafka_producer.py
* **Kafka Integration**: Utilizes the KafkaProducer class from the kafka library to interact with a Kafka server specified in the environment variables.
* **Data Generation**: Fetches random user data from the '[randomuser.me](https://randomuser.me/)' API using the requests library.
* **Data Transformation**: Transforms the raw user data into a structured format, including the user's name, gender, location details, encrypted email, date of birth, encrypted username, and encrypted password.
* **Encryption**: Implements encryption of sensitive information (email, username, password) using the Fernet symmetric encryption algorithm from the cryptography library.
* **Streaming Loop**: Executes a streaming loop that continuously retrieves, transforms, encrypts, and publishes user data to the Kafka topic. The streaming duration and pause intervals are configurable.

### kafka_consumer_s3.py
* **Kafka Integration**: Utilizes the KafkaConsumer class to consume messages from the Kafka topic, with the auto_offset_reset set to 'earliest' for processing all available messages.
* **Message Processing**: Processes each consumed message by decoding the JSON payload and extracting user information.
* **AWS S3 Integration**: Utilizes the boto3 library to interact with AWS S3, uploading the processed user data as a JSON file to a specified S3 bucket.

### kafka_consumer_mysql.py
* **Kafka Integration**: Utilizes the KafkaConsumer class to consume messages from the Kafka topic, with the auto_offset_reset set to 'earliest' for processing all available messages.
* **MySQL Database Integration**: Establishes a connection to a MySQL database using the mysql.connector library, with the database configuration details provided through environment variables.
* **Message Processing**: Defines a process_message method that parses the JSON payload from the Kafka message, extracts relevant user information, and inserts it into a MySQL database. Date of birth (dob_date) is converted from the provided format to the MySQL-compatible format.
* **Database Insertion**: Executes an SQL INSERT query to add user data to the 'users' table in the MySQL database. The query includes parameters for the user's name, gender, location details, encrypted email, date of birth, age, username, and password.

### Update the .env file according to yours configuration
```
KAFKA_SERVER = 'localhost:9092' # by default kafka runs on localhost:9092
TOPIC_NAME = 'users_topic' # we will use the topic that we created earlier
KEY = 'key for data encryption'
PAUSE_INTERVAL = 10 # there will be gap of 10 sec to call randomuserapi
STREAMING_DURATION = 120 # the streaming duration for kafka_producer is 2 mins

DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'users_db' # we will use the database that we created earlier
DB_USER = 'your_mysql_user'
DB_PASSWORD = 'your_password'

AWS_ACCESS_KEY_ID = 'your_aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'your_aws_secret_access_key'
AWS_REGION = 'your_aws_region'
S3_BUCKET_NAME = 'users-bucket' # we wil use the bucket we created earlier
AWS_URL='http://localhost:4566' # by default localstack runs on localhost:4566
```

If you are having difficulty with key for encryption use the following code and update the KEY in .env file.
```
from cryptography.fernet import Fernet
key = Fernet.generate_key()
```

---
---
In summary, this project showcases a robust data streaming pipeline that combines Kafka for real-time data transmission, encryption for securing sensitive information, and AWS S3 or MySQL database for durable storage.
