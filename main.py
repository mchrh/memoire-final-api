from fastapi import FastAPI, HTTPException, Request
import boto3
import time
import logging
import socket
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

DYNAMODB_REGION = 'eu-west-1'
dynamodb_client = boto3.client('dynamodb', region_name=DYNAMODB_REGION)
RATE_LIMIT_TABLE_NAME = 'api_rate_limits'
REQUEST_LIMIT = 10 # 5
WINDOW_SECONDS = 60

@app.middleware("http")
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
    logger.info("Root endpoint called")
    return {"status": "ok"}

@app.get("/test-rate-limit")
async def test_rate_limit():
    return {"message": "If you see this, you are within the rate limit!"}

@app.get("/healthz")
async def health_check():
    logger.info("====== Health check endpoint /healthz was CALLED! ======")
    response_payload = {"status": "healthy", "message": "API is operational"}
    logger.info(f"====== Health check /healthz responding with: {response_payload} (HTTP 200 OK) ======")
    return response_payload 

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"===> Incoming request: {request.method} {request.url.path} from {request.client}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"<=== Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application has started successfully!")

@app.get("/debug")
async def debug_info():
    import subprocess
    
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    
    try:
        metadata_uri = os.environ.get('ECS_CONTAINER_METADATA_URI_V4', 'Not found')
    except:
        metadata_uri = "Error getting metadata URI"
    
    return {
        "hostname": hostname,
        "container_ip": ip,
        "port": 8000,
        "metadata_uri": metadata_uri,
        "environment": dict(os.environ)
    }