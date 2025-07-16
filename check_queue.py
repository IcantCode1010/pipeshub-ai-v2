import asyncio
import sys
sys.path.append('/app/python')
from app.setups.indexing_setup import AppContainer

async def check_queue_status():
    container = AppContainer()
    from app.setups.indexing_setup import initialize_container
    await initialize_container(container)
    arango_service = await container.arango_service()
    
    # Check files by status
    query = '''
    FOR record IN records 
    COLLECT status = record.indexingStatus WITH COUNT INTO count
    RETURN { status, count }
    '''
    
    cursor = arango_service.db.aql.execute(query)
    results = list(cursor)
    
    print("File Processing Status Summary:")
    for result in results:
        print(f"- {result['status']}: {result['count']} files")
    
    # Check recent files
    recent_query = '''
    FOR record IN records 
    FILTER record.createdAtTimestamp > DATE_NOW() - 86400000
    SORT record.createdAtTimestamp DESC
    LIMIT 10
    RETURN {
        name: record.recordName,
        indexingStatus: record.indexingStatus,
        extractionStatus: record.extractionStatus,
        created: record.createdAtTimestamp
    }
    '''
    
    cursor = arango_service.db.aql.execute(recent_query)
    recent_results = list(cursor)
    
    print("\nRecent Files (last 24 hours):")
    for record in recent_results:
        print(f"- {record['name']} - Indexing: {record['indexingStatus']}, Extraction: {record['extractionStatus']}")

if __name__ == "__main__":
    asyncio.run(check_queue_status())
