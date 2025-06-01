# Implémentation API pour PFE

Implémentation initiale d'une API pour exploiter les données de notre data lakes incluant des rate limits et utilise DynamoDB sur AWS. 

## Features

- **FastAPI** 
- **Rate limiting**: 5 requêtes toutes les 60 secondes 
- **DynamoDB**: Pour store ces rates limits.
- **Logging**: Logs requests et rate limit 

## Endpoints

- `GET /`  
  Retourne un message d'acceuil.

- `GET /test-rate-limit`  
  Retourne un message si vous n'avez pas dépassé le rate limit.

#TODO: rajouter des endpoints

## Rate Limiting

- Chaque IP a droit à **5 requêtes toutes les 60 secondes**.
- Si la limite est atteinte, l'API retourne **HTTP 429 Too Many Requests**.

## Requirements

- Python 3.11
- FastAPI
- boto3
- AWS credentials with access to DynamoDB

## Environment Variables

- `DYNAMODB_REGION` (default: `eu-west-1`)
- `RATE_LIMIT_TABLE_NAME` (default: `api_rate_limits`)