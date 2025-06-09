from . import database as db
import logging

logger = logging.getLogger(__name__)

def get_all_companies(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT ticker, name, gics_sector FROM companies ORDER BY ticker")
        companies = cursor.fetchall()
        return [{"ticker": row[0], "name": row[1], "gics_sector": row[2]} for row in companies]

def get_financials_for_ticker(conn, ticker: str):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT date, price, volume, pe_ratio, revenue, debt 
            FROM price_data 
            WHERE ticker = %s 
            ORDER BY date DESC
        """, (ticker,))
        financials = cursor.fetchall()
        return [{
            "date": row[0], "price": row[1], "volume": row[2], 
            "pe_ratio": row[3], "revenue": row[4], "debt": row[5]
        } for row in financials]

def get_news_for_company(mongo_db_collection, company_name: str):
    news_articles = mongo_db_collection.find(
        {'company_name': company_name},
        {'_id': 0} 
    ).sort("published_date", -1).limit(20)

    return list(news_articles)