from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class Company(BaseModel):
    ticker: str
    name: str
    gics_sector: Optional[str] = None

    class Config:
        from_attributes = True

class CompanyDetails(Company):
    created_at: Optional[datetime] = None

class FinancialData(BaseModel):
    date: date
    price: Optional[float] = None
    volume: Optional[int] = None
    pe_ratio: Optional[float] = None
    revenue: Optional[float] = None
    debt: Optional[float] = None

    class Config:
        from_attributes = True

class NewsPublisher(BaseModel):
    href: Optional[str] = None
    title: str

class NewsArticle(BaseModel):
    title: str
    description: Optional[str] = None
    published_date: str 
    url: str
    publisher: NewsPublisher
    company_name: str 