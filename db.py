from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os

client = MongoClient(os.environ.get('MONGO'))
db = client.thingsTD
PDFVision = db.PDFVision