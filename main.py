from fastapi import FastAPI, HTTPException, Request
import boto3
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

DYNAMODB_REGION = 'eu-west-1'
dynamodb_client = boto3.client('dynamodb', region_name=DYNAMODB_REGION)
RATE_LIMIT_TABLE_NAME = 'api_rate_limits'
REQUEST_LIMIT = 10 # 5
WINDOW_SECONDS = 60

"""@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_identifier = request.client.host
    logger.info(f"Processing request for client: {client_identifier}")

    current_time = int(time.time())

    try:
        response = dynamodb_client.get_item(
            TableName=RATE_LIMIT_TABLE_NAME,
            Key={'user_id': {'S': client_identifier}}
        )

        item = response.get('Item')

        if item:
            request_count = int(item.get('request_count', {}).get('N', '0'))
            last_request_timestamp = int(item.get('last_request_timestamp', {}).get('N', '0'))

            if current_time - last_request_timestamp > WINDOW_SECONDS:
                request_count = 1  # Reset count for new window
            else:
                if request_count >= REQUEST_LIMIT:
                    logger.warning(f"Rate limit exceeded for {client_identifier}")
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                request_count += 1
        else:
            request_count = 1

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
        logger.error(f"Error interacting with DynamoDB for rate limiting: {e}")

    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "Hello! Your request has been processed."}

@app.get("/test-rate-limit")
async def test_rate_limit():
    return {"message": "If you see this, you are within the rate limit!"}"""

@app.get("/healthz")
async def health_check():
    logger.info("====== Health check endpoint /healthz was CALLED! ======")
    response_payload = {"status": "healthy", "message": "API is operational"}
    logger.info(f"====== Health check /healthz responding with: {response_payload} (HTTP 200 OK) ======")
    return response_payload 