 
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import json

# Init clients as above
cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)
container = cosmos_client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def get_billing_record(record_id, partition_key):
    try:
        # First, try Cosmos DB
        item = container.read_item(item=record_id, partition_key=partition_key)
        return item
    except Exception as e:
        # Not found or archived
        blob_name = f"{partition_key}/{record_id}.json"
        try:
            blob_client = blob_container_client.get_blob_client(blob_name)
            stream = blob_client.download_blob()
            data = json.loads(stream.readall())
            return data
        except Exception:
            raise Exception("Record not found in hot or cold storage.")
