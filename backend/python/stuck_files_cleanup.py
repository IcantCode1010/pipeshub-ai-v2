#!/usr/bin/env python3
"""
Stuck Files Cleanup Script
This script helps identify and resolve files that are stuck in processing state.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.config.configuration_service import ConfigurationService
from app.config.utils.named_constants.arangodb_constants import (
    CollectionNames,
    ProgressStatus,
)
from app.core.ai_arango_service import ArangoService
from app.core.celery_app import CeleryApp
from app.core.redis_scheduler import RedisScheduler
from app.services.kafka_consumer import KafkaConsumerManager


class StuckFilesCleanup:
    """
    A comprehensive tool to identify and resolve files stuck in processing state.
    """
    
    def __init__(self, config_service: ConfigurationService, logger: logging.Logger):
        self.config_service = config_service
        self.logger = logger
        self.arango_service = None
        self.redis_scheduler = None
        
    async def initialize(self):
        """Initialize services"""
        try:
            self.logger.info("🚀 Initializing cleanup service...")
            
            # Initialize ArangoDB service
            self.arango_service = ArangoService(self.logger, self.config_service)
            await self.arango_service.initialize()
            
            # Initialize Redis scheduler
            redis_config = await self.config_service.get_config("redis")
            redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config.get('db', 0)}"
            self.redis_scheduler = RedisScheduler(redis_url, self.logger)
            
            self.logger.info("✅ Services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize services: {str(e)}")
            raise

    async def analyze_stuck_files(self) -> Dict:
        """
        Analyze files that are stuck in processing state.
        
        Returns:
            Dict: Analysis results including counts and details
        """
        try:
            self.logger.info("🔍 Analyzing stuck files...")
            
            # Get all files with IN_PROGRESS status
            in_progress_records = await self.arango_service.get_documents_by_status(
                CollectionNames.RECORDS.value,
                ProgressStatus.IN_PROGRESS.value
            )
            
            # Get all files with NOT_STARTED status (older than 30 minutes)
            not_started_records = await self.arango_service.get_documents_by_status(
                CollectionNames.RECORDS.value,
                ProgressStatus.NOT_STARTED.value
            )
            
            # Get all files with FAILED status
            failed_records = await self.arango_service.get_documents_by_status(
                CollectionNames.RECORDS.value,
                ProgressStatus.FAILED.value
            )
            
            # Analyze timing for stuck files
            current_time = datetime.now()
            stuck_threshold = timedelta(minutes=30)  # Files stuck for more than 30 minutes
            
            truly_stuck_in_progress = []
            old_not_started = []
            
            for record in in_progress_records:
                updated_at = record.get("updatedAtTimestamp")
                if updated_at:
                    # Convert timestamp to datetime
                    updated_datetime = datetime.fromtimestamp(updated_at / 1000)
                    if current_time - updated_datetime > stuck_threshold:
                        truly_stuck_in_progress.append({
                            "record_id": record["_key"],
                            "record_name": record.get("recordName", "Unknown"),
                            "updated_at": updated_datetime.isoformat(),
                            "stuck_duration": str(current_time - updated_datetime),
                            "reason": record.get("reason", "No reason provided")
                        })
            
            for record in not_started_records:
                created_at = record.get("createdAtTimestamp")
                if created_at:
                    created_datetime = datetime.fromtimestamp(created_at / 1000)
                    if current_time - created_datetime > stuck_threshold:
                        old_not_started.append({
                            "record_id": record["_key"],
                            "record_name": record.get("recordName", "Unknown"),
                            "created_at": created_datetime.isoformat(),
                            "age": str(current_time - created_datetime),
                            "reason": record.get("reason", "No reason provided")
                        })
            
            analysis = {
                "total_in_progress": len(in_progress_records),
                "truly_stuck_in_progress": len(truly_stuck_in_progress),
                "stuck_in_progress_details": truly_stuck_in_progress,
                "total_not_started": len(not_started_records),
                "old_not_started": len(old_not_started),
                "old_not_started_details": old_not_started,
                "total_failed": len(failed_records),
                "failed_details": [
                    {
                        "record_id": record["_key"],
                        "record_name": record.get("recordName", "Unknown"),
                        "reason": record.get("reason", "No reason provided")
                    }
                    for record in failed_records[:10]  # Show first 10 failed records
                ],
                "analysis_timestamp": current_time.isoformat()
            }
            
            self.logger.info(f"📊 Analysis complete:")
            self.logger.info(f"   - Total IN_PROGRESS: {analysis['total_in_progress']}")
            self.logger.info(f"   - Truly stuck IN_PROGRESS: {analysis['truly_stuck_in_progress']}")
            self.logger.info(f"   - Old NOT_STARTED: {analysis['old_not_started']}")
            self.logger.info(f"   - Total FAILED: {analysis['total_failed']}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing stuck files: {str(e)}")
            raise

    async def cleanup_stuck_files(self, dry_run: bool = True) -> Dict:
        """
        Clean up files that are stuck in processing state.
        
        Args:
            dry_run (bool): If True, only report what would be done without making changes
            
        Returns:
            Dict: Cleanup results
        """
        try:
            self.logger.info(f"🧹 Starting cleanup (dry_run={dry_run})...")
            
            # Get analysis first
            analysis = await self.analyze_stuck_files()
            
            cleanup_results = {
                "dry_run": dry_run,
                "cleanup_timestamp": datetime.now().isoformat(),
                "actions_taken": [],
                "errors": []
            }
            
            # Clean up truly stuck IN_PROGRESS files
            stuck_in_progress = analysis["stuck_in_progress_details"]
            if stuck_in_progress:
                self.logger.info(f"🔄 Processing {len(stuck_in_progress)} stuck IN_PROGRESS files...")
                
                for file_info in stuck_in_progress:
                    try:
                        record_id = file_info["record_id"]
                        
                        if not dry_run:
                            await self._update_document_status(
                                record_id=record_id,
                                indexing_status=ProgressStatus.FAILED.value,
                                extraction_status=ProgressStatus.FAILED.value,
                                reason="Document processing interrupted - cleaned up by stuck files script"
                            )
                        
                        action = {
                            "action": "mark_as_failed",
                            "record_id": record_id,
                            "record_name": file_info["record_name"],
                            "stuck_duration": file_info["stuck_duration"],
                            "executed": not dry_run
                        }
                        cleanup_results["actions_taken"].append(action)
                        
                    except Exception as e:
                        error = {
                            "record_id": file_info["record_id"],
                            "error": str(e)
                        }
                        cleanup_results["errors"].append(error)
                        self.logger.error(f"❌ Error processing {file_info['record_id']}: {str(e)}")
            
            # Clean up old NOT_STARTED files (retry them)
            old_not_started = analysis["old_not_started_details"]
            if old_not_started:
                self.logger.info(f"🔄 Processing {len(old_not_started)} old NOT_STARTED files...")
                
                for file_info in old_not_started:
                    try:
                        record_id = file_info["record_id"]
                        
                        if not dry_run:
                            # Try to requeue the file for processing
                            await self._requeue_file_for_processing(record_id)
                        
                        action = {
                            "action": "requeue_for_processing",
                            "record_id": record_id,
                            "record_name": file_info["record_name"],
                            "age": file_info["age"],
                            "executed": not dry_run
                        }
                        cleanup_results["actions_taken"].append(action)
                        
                    except Exception as e:
                        error = {
                            "record_id": file_info["record_id"],
                            "error": str(e)
                        }
                        cleanup_results["errors"].append(error)
                        self.logger.error(f"❌ Error requeuing {file_info['record_id']}: {str(e)}")
            
            # Report results
            total_actions = len(cleanup_results["actions_taken"])
            total_errors = len(cleanup_results["errors"])
            
            if dry_run:
                self.logger.info(f"📋 DRY RUN COMPLETE: Would perform {total_actions} actions")
            else:
                self.logger.info(f"✅ CLEANUP COMPLETE: Performed {total_actions} actions with {total_errors} errors")
            
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {str(e)}")
            raise

    async def _update_document_status(
        self,
        record_id: str,
        indexing_status: str,
        extraction_status: str,
        reason: str = None,
    ) -> None:
        """Update document status in Arango"""
        try:
            record = await self.arango_service.get_document(
                record_id, CollectionNames.RECORDS.value
            )
            if not record:
                self.logger.error(f"❌ Record {record_id} not found for status update")
                return

            doc = dict(record)
            if doc.get("extractionStatus") == ProgressStatus.COMPLETED.value:
                extraction_status = ProgressStatus.COMPLETED.value
            doc.update(
                {
                    "indexingStatus": indexing_status,
                    "extractionStatus": extraction_status,
                    "updatedAtTimestamp": int(datetime.now().timestamp() * 1000),
                }
            )

            if reason:
                doc["reason"] = reason

            docs = [doc]
            await self.arango_service.batch_upsert_nodes(
                docs, CollectionNames.RECORDS.value
            )
            self.logger.info(f"✅ Updated document status for record {record_id}")

        except Exception as e:
            self.logger.error(f"❌ Failed to update document status: {str(e)}")
            raise

    async def _requeue_file_for_processing(self, record_id: str) -> None:
        """Requeue a file for processing by updating its status"""
        try:
            record = await self.arango_service.get_document(
                record_id, CollectionNames.RECORDS.value
            )
            if not record:
                self.logger.error(f"❌ Record {record_id} not found for requeuing")
                return

            doc = dict(record)
            doc.update(
                {
                    "indexingStatus": ProgressStatus.NOT_STARTED.value,
                    "extractionStatus": ProgressStatus.NOT_STARTED.value,
                    "updatedAtTimestamp": int(datetime.now().timestamp() * 1000),
                    "reason": "Requeued by stuck files cleanup script"
                }
            )

            docs = [doc]
            await self.arango_service.batch_upsert_nodes(
                docs, CollectionNames.RECORDS.value
            )
            self.logger.info(f"✅ Requeued record {record_id} for processing")

        except Exception as e:
            self.logger.error(f"❌ Failed to requeue record: {str(e)}")
            raise

    async def check_system_health(self) -> Dict:
        """
        Check the overall health of the file processing system.
        
        Returns:
            Dict: System health information
        """
        try:
            self.logger.info("🏥 Checking system health...")
            
            # Get processing statistics
            all_statuses = [
                ProgressStatus.NOT_STARTED.value,
                ProgressStatus.IN_PROGRESS.value,
                ProgressStatus.COMPLETED.value,
                ProgressStatus.FAILED.value,
                ProgressStatus.FILE_TYPE_NOT_SUPPORTED.value,
                ProgressStatus.AUTO_INDEX_OFF.value
            ]
            
            status_counts = {}
            for status in all_statuses:
                records = await self.arango_service.get_documents_by_status(
                    CollectionNames.RECORDS.value, status
                )
                status_counts[status] = len(records)
            
            # Calculate health metrics
            total_files = sum(status_counts.values())
            completed_files = status_counts.get(ProgressStatus.COMPLETED.value, 0)
            failed_files = status_counts.get(ProgressStatus.FAILED.value, 0)
            in_progress_files = status_counts.get(ProgressStatus.IN_PROGRESS.value, 0)
            
            success_rate = (completed_files / total_files * 100) if total_files > 0 else 0
            failure_rate = (failed_files / total_files * 100) if total_files > 0 else 0
            
            # Check for potential issues
            issues = []
            if in_progress_files > 100:
                issues.append(f"High number of files in progress: {in_progress_files}")
            if failure_rate > 10:
                issues.append(f"High failure rate: {failure_rate:.1f}%")
            if success_rate < 80:
                issues.append(f"Low success rate: {success_rate:.1f}%")
            
            health_info = {
                "timestamp": datetime.now().isoformat(),
                "total_files": total_files,
                "status_breakdown": status_counts,
                "metrics": {
                    "success_rate": f"{success_rate:.1f}%",
                    "failure_rate": f"{failure_rate:.1f}%",
                    "completion_rate": f"{(completed_files / total_files * 100):.1f}%" if total_files > 0 else "0%"
                },
                "issues": issues,
                "health_status": "HEALTHY" if not issues else "NEEDS_ATTENTION"
            }
            
            self.logger.info(f"📊 System Health Summary:")
            self.logger.info(f"   - Total files: {total_files}")
            self.logger.info(f"   - Success rate: {success_rate:.1f}%")
            self.logger.info(f"   - Failure rate: {failure_rate:.1f}%")
            self.logger.info(f"   - Health status: {health_info['health_status']}")
            
            if issues:
                self.logger.warning("⚠️ Issues detected:")
                for issue in issues:
                    self.logger.warning(f"   - {issue}")
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"❌ Error checking system health: {str(e)}")
            raise

    async def save_report(self, data: Dict, filename: str = None) -> str:
        """Save report data to a JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stuck_files_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"📄 Report saved to: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Error saving report: {str(e)}")
            raise


async def main():
    """Main function to run the stuck files cleanup"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration service
        config_service = ConfigurationService(logger)
        
        # Initialize cleanup service
        cleanup_service = StuckFilesCleanup(config_service, logger)
        await cleanup_service.initialize()
        
        # Check system health first
        logger.info("=" * 60)
        logger.info("SYSTEM HEALTH CHECK")
        logger.info("=" * 60)
        health_info = await cleanup_service.check_system_health()
        
        # Analyze stuck files
        logger.info("=" * 60)
        logger.info("STUCK FILES ANALYSIS")
        logger.info("=" * 60)
        analysis = await cleanup_service.analyze_stuck_files()
        
        # Ask user for action
        if analysis["truly_stuck_in_progress"] > 0 or analysis["old_not_started"] > 0:
            logger.info("=" * 60)
            logger.info("CLEANUP OPTIONS")
            logger.info("=" * 60)
            
            print("\nFound files that may need attention:")
            print(f"  - {analysis['truly_stuck_in_progress']} files stuck in IN_PROGRESS state")
            print(f"  - {analysis['old_not_started']} old files in NOT_STARTED state")
            
            print("\nOptions:")
            print("  1. Perform dry run (show what would be done)")
            print("  2. Perform actual cleanup")
            print("  3. Save report and exit")
            print("  4. Exit without action")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                logger.info("=" * 60)
                logger.info("DRY RUN CLEANUP")
                logger.info("=" * 60)
                cleanup_results = await cleanup_service.cleanup_stuck_files(dry_run=True)
                
            elif choice == "2":
                logger.info("=" * 60)
                logger.info("ACTUAL CLEANUP")
                logger.info("=" * 60)
                cleanup_results = await cleanup_service.cleanup_stuck_files(dry_run=False)
                
            elif choice == "3":
                report_data = {
                    "health_info": health_info,
                    "analysis": analysis
                }
                filename = await cleanup_service.save_report(report_data)
                logger.info(f"Report saved to {filename}")
                return
                
            else:
                logger.info("Exiting without action")
                return
            
            # Save comprehensive report
            report_data = {
                "health_info": health_info,
                "analysis": analysis,
                "cleanup_results": cleanup_results
            }
            filename = await cleanup_service.save_report(report_data)
            
        else:
            logger.info("✅ No stuck files detected!")
            
            # Save health report
            filename = await cleanup_service.save_report(health_info, "system_health_report.json")
        
        logger.info("=" * 60)
        logger.info("CLEANUP COMPLETE")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Script failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 