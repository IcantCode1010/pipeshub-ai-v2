import asyncio
import sys
sys.path.append('/app/python')
from app.setups.indexing_setup import AppContainer

async def check_processing_status():
    container = AppContainer()
    from app.setups.indexing_setup import initialize_container
    await initialize_container(container)
    arango_service = await container.arango_service()
    
    query = '''
    FOR record IN records 
    FILTER record.indexingStatus == "IN_PROGRESS" OR record.extractionStatus == "IN_PROGRESS"
    RETURN {
        id: record._key,
        name: record.recordName,
        indexingStatus: record.indexingStatus,
        extractionStatus: record.extractionStatus,
        created: record.createdAtTimestamp,
        updated: record.updatedAtTimestamp
    }
    '''
    
    cursor = arango_service.db.aql.execute(query)
    results = list(cursor)
    
    print(f'Files currently in processing: {len(results)}')
    for record in results:
        print(f'- {record["name"]} (ID: {record["id"]}) - Indexing: {record["indexingStatus"]}, Extraction: {record["extractionStatus"]}')

if __name__ == "__main__":
    asyncio.run(check_processing_status())
