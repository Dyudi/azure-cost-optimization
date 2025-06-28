import datetime
import logging
import json
import os

from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient

# ENV VARS
COSMOS_URL = os.environ['COSMOS_URL']
COSMOS_KEY = os.environ['COSMOS_KEY']
COSMOS_DB = os.environ['COSMOS_DB']
COSMOS_CONTAINER = os.environ['COSMOS_CONTAINER']
BLOB_CONN_STR = os.environ['BLOB_CONN_STR']
BLOB_CONTAINER = os.environ['BLOB_CONTAINER']

# Initialize clients
cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = cosmos_client.get_database_client(COSMOS_DB)
container = database.get_container_client(COSMOS_CONTAINER)

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def main(timer):
    logging.info('Migration function started.')

    cutoff_date = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()

    query = "SELECT * FROM c WHERE c.timestamp < @cutoff"
    params = [{"name":"@cutoff","value":cutoff_date}]
    old_records = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    for record in old_records:
        record_id = record['id']
        partition_key = record['partitionKey']

        # Serialize and store in blob
        blob_name = f"{partition_key}/{record_id}.json"
        blob_data = json.dumps(record)
        blob_container_client.upload_blob(name=blob_name, data=blob_data, overwrite=True)

        # Delete from Cosmos DB (or alternatively, set "archived":true)
        container.delete_item(item=record_id, partition_key=partition_key)
	#If you prefer not to delete immediately, replace this line:
	#record['archived'] = True
	#container.upsert_item(record)

        logging.info(f"Migrated and deleted record {record_id}")

    logging.info('Migration function completed.')
 
