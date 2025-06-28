# Managing Billing Records in Azure Serverless Architecture
Implementation Steps
- Step 1 :- Identify and Migrate Cold Data
- Step 2 :- Blob Storage Configuration
- Step 3 :- Transparent Access Logic
- Step 4 :- Zero Downtime Deployment
- Azure Function to Migrate Old Records
  This function can run on a timer trigger. The records older than 3 months in the Cosmos DB can store to Blob storage. Then optionally deletes them from Cosmos DB (or marks as archived).
