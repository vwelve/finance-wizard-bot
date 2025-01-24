# database/mongo_client.py
from pymongo import MongoClient
from config import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client["FINANCE_BOT"]