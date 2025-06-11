from fastapi.testclient import TestClient
from app.main import app, get_db_conn, get_mongo_news_collection 
import pytest 

client = TestClient(app)

def override_get_db_conn():
    try:
        yield "fake_db_connection" 
    finally:
        print("Fake DB connection closed")

def override_get_mongo_news_collection():
    class MockMongoCollection:
        def find(self, *args, **kwargs):
            return self 

        def sort(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return []

    try:
        yield MockMongoCollection()
    finally:
        print("Fake Mongo connection closed")

app.dependency_overrides[get_db_conn] = override_get_db_conn
app.dependency_overrides[get_mongo_news_collection] = override_get_mongo_news_collection

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "API is operational"}
    print("✓ /healthz endpoint test passed!")

def test_read_companies_success(monkeypatch):
    test_company_data = [
        {"ticker": "TEST1", "name": "Test Company One", "gics_sector": "Technology"},
        {"ticker": "TEST2", "name": "Test Company Two", "gics_sector": "Finance"}
    ]
    
    def fake_get_all_companies(conn):
        print("--> Called fake_get_all_companies")
        return test_company_data

    monkeypatch.setattr("app.crud.get_all_companies", fake_get_all_companies)

    response = client.get("/v1/companies")

    assert response.status_code == 200
    assert response.json() == test_company_data
    print("✓ /v1/companies endpoint test passed!")

def test_read_financials_not_found(monkeypatch):
    def fake_get_financials(conn, ticker):
        print(f"--> Called fake_get_financials for ticker {ticker}, returning no data")
        return []

    monkeypatch.setattr("app.crud.get_financials_for_ticker", fake_get_financials)

    response = client.get("/v1/companies/NONEXISTENT/financials")

    assert response.status_code == 404
    assert response.json() == {"detail": "Financial data not found for ticker 'NONEXISTENT'"}
    print("✓ /v1/companies/{ticker}/financials 404 test passed!")