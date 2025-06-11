# Implémentation API pour PFE

Implémentation d'une API pour exploiter les données de notre data lakes incluant des rate limits et utilise DynamoDB sur AWS. 

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

- `GET v1/companies`
  Retourne les nom des sociétes, leur ticker ainsi que le secteur auxquelles elles appartiennent.

- `GET v1/companies/{ticker}/financials`
  Retourne une série temporelle sur plus de 5 ans avec la date, le prix, le volume échangé, ratio P/E, revenues et dette pour un ticker donné.

- `GET v1/companies/{ticker}/news`
  Retourne des actualités sur la société au format JSON pour un ticker donné. 

## Testing 

Nous avons inclus des tests unitaires pour vérifier le bon fonctionnement de nos endpoints. Les tests utilisent la librarie pytest. Il suffit de pytest -v. 

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