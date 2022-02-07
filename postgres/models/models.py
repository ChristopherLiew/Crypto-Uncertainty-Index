"""
SQLAlchemy Relational Models
"""

from sqlalchemy import (
    Column,
    BIGINT,
    INTEGER,
    VARCHAR,
    DATE,
    DECIMAL
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AssetPriceTable(Base):

    __tablename__ = "asset_prices"

    ticker = Column(VARCHAR, primary_key=True)
    date = Column(DATE, primary_key=True)
    open = Column(DECIMAL)
    close = Column(DECIMAL)
    high = Column(DECIMAL)
    low = Column(DECIMAL)
    adj_close = Column(DECIMAL)
    volume = Column(BIGINT)


class UcryIndexTable(Base):

    __tablename__ = "ucry_index"

    name = Column(VARCHAR, primary_key=True)
    type = Column(DATE, primary_key=True)
    start_date = Column(DATE, primary_key=True)
    end_date = Column(DATE)
    doc_count = Column(INTEGER)
    index_value = Column(DECIMAL)
