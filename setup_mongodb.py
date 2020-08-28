from flask import Flask, json, Response, request
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/test')
db = client['test_database']
collection = db.test_collection

new_profile = {'user_id': 213, 'name': 'Drew'}
result = db.missed.insert_one(new_profile)