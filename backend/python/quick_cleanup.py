#!/usr/bin/env python3
"""
Quick Cleanup Script for Stuck Files
Run this to immediately resolve files stuck in processing state.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config.configuration_service import ConfigurationService
from app.config.utils.named_constants.arangodb_constants import CollectionNames, ProgressStatus
from app.core.ai_arango_service import ArangoService
from app.utils.logger import setup_logger


async def cleanup_stuck_files():
    """Clean up files stuck in processing state"""
    
    # Setup logger
    logger = setup_logger(__name__)
    logger.info("🚀 Starting quick cleanup of stuck files...")
    
    try:
        # Initialize configuration service
        config_service = ConfigurationService(logger)
        
        # Initialize ArangoDB service
        arango_service = ArangoService(logger, config_service)
        await arango_service.initialize()
        
        # Get all documents with IN_PROGRESS status
        logger.info("🔍 Finding files stuck in IN_PROGRESS state...")
        stuck_records = await arango_service.get_documents_by_status(
            CollectionNames.RECORDS.value,
            ProgressStatus.IN_PROGRESS.value
        )
        
        if not stuck_records:
            logger.info("✅ No files found stuck in IN_PROGRESS state")
            return
        
        logger.warning(f"Found {len(stuck_records)} files stuck in IN_PROGRESS state")
        
        # Update each stuck file to FAILED status
        for record in stuck_records:
            try:
                record_id = record["_key"]
                record_name = record.get("recordName", "Unknown")
                
                logger.info(f"🔄 Processing stuck file: {record_name} ({record_id})")
                
                # Update document status
                doc = dict(record)
                doc.update({
                    "indexingStatus": ProgressStatus.FAILED.value,
                    "extractionStatus": ProgressStatus.FAILED.value,
                    "reason": "Document processing interrupted - cleaned up by quick cleanup script"
                })
                
                docs = [doc]
                success = await arango_service.batch_upsert_nodes(
                    docs, CollectionNames.RECORDS.value
                )
                
                if success:
                    logger.info(f"✅ Successfully updated {record_name} to FAILED status")
                else:
                    logger.error(f"❌ Failed to update {record_name}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing record {record.get('_key', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"✅ Cleanup completed! Processed {len(stuck_records)} stuck files")
        
        # Show summary of all file statuses
        logger.info("📊 Current file status summary:")
        statuses = [
            ProgressStatus.NOT_STARTED.value,
            ProgressStatus.IN_PROGRESS.value,
            ProgressStatus.COMPLETED.value,
            ProgressStatus.FAILED.value,
            ProgressStatus.FILE_TYPE_NOT_SUPPORTED.value,
            ProgressStatus.AUTO_INDEX_OFF.value
        ]
        
        for status in statuses:
            records = await arango_service.get_documents_by_status(
                CollectionNames.RECORDS.value, status
            )
            count = len(records)
            logger.info(f"   {status}: {count} files")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(cleanup_stuck_files()) 