from database import engine, Base
from models import ProductEconomics

Base.metadata.create_all(bind=engine)