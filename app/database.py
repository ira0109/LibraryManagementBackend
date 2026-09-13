from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

database_url = make_url(settings.DATABASE_URL)
if database_url.drivername in ("mysql", "mysql+mysqldb"):
    database_url = database_url.set(drivername="mysql+pymysql")

url_query = dict(database_url.query)
url_ssl_mode = url_query.pop("ssl-mode", "").upper()
database_url = database_url.set(query=url_query)

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

ssl_required = settings.DATABASE_SSL_MODE.upper() == "REQUIRED" or url_ssl_mode == "REQUIRED"
if database_url.drivername == "mysql+pymysql" and ssl_required:
    engine_kwargs["connect_args"] = {"ssl": {}}

engine = create_engine(
    database_url,
    **engine_kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()