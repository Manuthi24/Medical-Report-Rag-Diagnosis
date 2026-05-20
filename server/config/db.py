from dotenv import load_dotenv
import os


load_dotenv()

# Mock in-memory database
class MockCollection:
    def __init__(self):
        self.data = {}
        self.counter = 0
    
    def insert_one(self, doc):
        self.counter += 1
        doc['_id'] = self.counter
        self.data[self.counter] = doc.copy()
        return type('obj', (object,), {'inserted_id': self.counter})()
    
    def find_one(self, query):
        for doc in self.data.values():
            match = True
            for key, val in query.items():
                if doc.get(key) != val:
                    match = False
                    break
            if match:
                return doc
        return None
    
    def find(self, query):
        results = []
        for doc in self.data.values():
            match = True
            for key, val in query.items():
                if doc.get(key) != val:
                    match = False
                    break
            if match:
                results.append(doc)
        return results


users_collection = MockCollection()
reports_collection = MockCollection()
diagnosis_collection = MockCollection()

# Pre-populate reports from MongoDB
reports_data = [
    {
        "_id": "6983aa80fe660e07ceef999b",
        "doc_id": "1678c8e9-e4f4-42e9-8b89-07fcf8308148",
        "filename": "sample-report.pdf",
        "uploader": "Manuthi",
        "num_chunks": 4,
        "upload_time": 1770236544.908292
    },
    {
        "_id": "6983aeb884f1f96244c23e5b",
        "doc_id": "78b5ddfc-506e-4b7e-8042-eaf4dd2f53fb",
        "filename": "sample-report.pdf",
        "uploader": "Manuthi",
        "num_chunks": 4,
        "upload_time": 1770237624.5388966
    },
    {
        "_id": "6983afd5579cd74de338fd7f",
        "doc_id": "d8486846-5125-4489-b036-dcae1e24961c",
        "filename": "sample-report.pdf",
        "uploader": "Manuthi",
        "num_chunks": 4,
        "upload_time": 1770237909.6756556
    },
    {
        "_id": "6983b1a05cd2ed6d735129af",
        "doc_id": "2cbe882e-579c-4da0-b761-7f4345446327",
        "filename": "sample-report.pdf",
        "uploader": "Manuthi",
        "num_chunks": 4,
        "upload_time": 1770238368.1625042
    }
]

for report in reports_data:
    reports_collection.data[report["_id"]] = report

print("Using mock in-memory database with pre-loaded reports")