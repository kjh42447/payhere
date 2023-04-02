from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.environ.get("DB_URL")

class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn