# In app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from typing import List
from . import crud, schemas, database as db
import time
import logging
import socket
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FinData API")

DYNAMODB_REGION = 'eu-west-1'
dynamodb_client = boto3.client('dynamodb', region_name=DYNAMODB_REGION)
RATE_LIMIT_TABLE_NAME = 'api_rate_limits'
REQUEST_LIMIT = 10
WINDOW_SECONDS = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == '/healthz':
        response = await call_next(request)
        return response

    client_identifier = request.client.host
    current_time = int(time.time())

    try:
        # Your full rate-limiting logic here...
        dynamo_response = dynamodb_client.get_item(
            TableName=RATE_LIMIT_TABLE_NAME,
            Key={'user_id': {'S': client_identifier}}
        )
        item = dynamo_response.get('Item')
        request_count = 1
        if item:
            last_request_timestamp = int(item.get('last_request_timestamp', {}).get('N', '0'))
            if current_time - last_request_timestamp > WINDOW_SECONDS:
                request_count = 1 
            else:
                current_count = int(item.get('request_count', {}).get('N', '0'))
                if current_count >= REQUEST_LIMIT:
                    logger.warning(f"Rate limit exceeded for {client_identifier}")
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                request_count = current_count + 1
        
        dynamodb_client.put_item(
            TableName=RATE_LIMIT_TABLE_NAME,
            Item={
                'user_id': {'S': client_identifier},
                'request_count': {'N': str(request_count)},
                'last_request_timestamp': {'N': str(current_time)}
            }
        )
        logger.info(f"Request count for {client_identifier}: {request_count}")

    except Exception as e:
        logger.error(f"Error in rate-limiting middleware interacting with DynamoDB: {e}")

    response = await call_next(request)
    return response

def get_db_conn():
    conn = db.get_postgres_conn()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection not available")
    try:
        yield conn
    finally:
        db.put_postgres_conn(conn)

@app.get("/healthz", tags=["Status"])
async def health_check():
    return {"status": "healthy"}

@app.get("/", response_model=schemas.Company, tags=["Root"]) 
def read_root(conn = Depends(get_db_conn)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT ticker, name, gics_sector FROM companies LIMIT 1")
        company = cursor.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="No companies found")
        return {"ticker": company[0], "name": company[1], "gics_sector": company[2]}

@app.get("/v1/companies", response_model=List[schemas.Company], tags=["Companies"])
def read_companies(conn = Depends(get_db_conn)):
    companies = crud.get_all_companies(conn)
    return companies

@app.get("/v1/companies/{ticker}/financials", response_model=List[schemas.FinancialData], tags=["Companies"])
def read_financials(ticker: str, conn = Depends(get_db_conn)):
    financials = crud.get_financials_for_ticker(conn, ticker=ticker)
    if not financials:
        raise HTTPException(status_code=404, detail=f"Financial data not found for ticker '{ticker}'")
    return financials