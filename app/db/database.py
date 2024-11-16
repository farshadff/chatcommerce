from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URL = "postgresql://username:password@localhost/dbname"  # PostgreSQL
# DATABASE_URL = "mysql+pymysql://username:password@localhost/dbname"  # MySQL

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)
