

from pymongo import MongoClient
import os


def get_ads_targetings():
    client = MongoClient(os.environ['mongo_url'], maxPoolSize=200)
    db = client.get_database(os.environ['db_name'])
    colles_targetings = db.targetings.find({}, {'_id': 0, 'is_good': 1, 'targeting': 1})
    client.close()
    return colles_targetings


def update_adsets(old_adset_id, new_adset_id, adset_data):
    client = MongoClient(os.environ['mongo_url'], maxPoolSize=200)
    db = client.get_database(os.environ['db_name'])
    db.baits.update({'adset_id': old_adset_id}, {'$set': {'adset_id': new_adset_id, 'adset_data': adset_data}}, upsert=True)
    client.close()


