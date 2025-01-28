import csv
import os
from pymongo import MongoClient


mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_INITDB_DATABASE")
collection_name = os.getenv("MONGO_INITDB_COLLECTION")

client = MongoClient(mongo_uri)
db = client.get_database(str(db_name))
collection = db.get_collection(str(collection_name))

# Чтение CSV файла
csv_file = "final_products.csv"



def parse_components(components_str):
    components = components_str.split(",")
    return [component.strip() for component in components]



with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        row['components'] = parse_components(row['components'])

        collection.insert_one({
            "product_name": row["product_name"],
            "product_link": row["product_link"],
            "product_img_link": row["product_img_link"],
            "category": row["category"],
            "components": row["components"]
        })

print("Данные успешно загружены в MongoDB.")
