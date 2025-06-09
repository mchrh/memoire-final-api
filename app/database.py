import boto3
import json
import psycopg2
from psycopg2 import pool
import pymongo
import os

secrets_client = boto3.client('secretsmanager', region_name='eu-west-1') 

RDS_HOST = "memoire-postgres-db.cfe820e68ynv.eu-west-1.rds.amazonaws.com" 
RDS_DB_NAME = "financial_data"
RDS_USER = "thesisadmin"
RDS_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:920372996939:secret:thesis/rds/password-qeXZHF" 
rds_secret_payload = secrets_client.get_secret_value(SecretId=RDS_SECRET_ARN)
RDS_PASSWORD = json.loads(rds_secret_payload['SecretString'])['password']

MONGO_SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:920372996939:secret:thesis/mongodb/uri-1uhjbA" 
mongo_secret_payload = secrets_client.get_secret_value(SecretId=MONGO_SECRET_ARN)
MONGO_URI = json.loads(mongo_secret_payload['SecretString'])['mongodb_uri']

try:
    postgres_pool = psycopg2.pool.SimpleConnectionPool(
        1, 5, 
        host=RDS_HOST,
        database=RDS_DB_NAME,
        user=RDS_USER,
        password=RDS_PASSWORD
    )

    mongo_client = pymongo.MongoClient(MONGO_URI)
    mongo_db = mongo_client['news-db'] 

except Exception as e:
    postgres_pool = None
    mongo_client = None
    mongo_db = None
    print(f"ERROR: Could not connect to databases -> {e}")

def get_postgres_conn():
    if postgres_pool:
        return postgres_pool.getconn()
    return None

def put_postgres_conn(conn):
    if postgres_pool:
        postgres_pool.putconn(conn)