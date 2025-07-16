# Stuck Files Resolution Guide

## Overview
This guide helps you resolve files that are stuck in processing state in your PipesHub AI system.

## Understanding the Issue

### File Processing States
Your system tracks files through these states:
- **NOT_STARTED**: File uploaded but processing hasn't begun
- **IN_PROGRESS**: File is currently being processed
- **COMPLETED**: File processing finished successfully
- **FAILED**: File processing failed
- **FILE_TYPE_NOT_SUPPORTED**: File type not supported
- **AUTO_INDEX_OFF**: Manual sync required

### Common Causes of Stuck Files
1. **Application Crashes**: If the system crashes while processing files, they remain in IN_PROGRESS state
2. **Kafka Consumer Issues**: The message processing system may have stopped
3. **Database Connection Problems**: Network issues affecting ArangoDB
4. **Memory/Resource Constraints**: System running out of resources during processing
5. **Celery Worker Problems**: Background task processing issues

## Quick Resolution (Recommended)

### For Windows Users
1. Open PowerShell as Administrator
2. Navigate to the backend/python directory:
   ```powershell
   cd C:\projects\pipeshub-v2\pipeshub-ai\backend\python
   ```
3. Run the cleanup script:
   ```powershell
   .\cleanup_stuck_files.ps1
   ```

### For Linux/Mac Users
1. Open Terminal
2. Navigate to the backend/python directory:
   ```bash
   cd /path/to/pipeshub-ai/backend/python
   ```
3. Make the script executable (if needed):
   ```bash
   chmod +x cleanup_stuck_files.sh
   ```
4. Run the cleanup script:
   ```bash
   ./cleanup_stuck_files.sh
   ```

### Manual Python Execution
If the scripts don't work, run directly:
```bash
cd backend/python
python quick_cleanup.py
```

## What the Cleanup Script Does

1. **Identifies Stuck Files**: Finds files in IN_PROGRESS state
2. **Updates Status**: Changes stuck files to FAILED status with a clear reason
3. **Provides Summary**: Shows counts of files in each status
4. **Safe Operation**: Only updates status, doesn't delete files

## After Running Cleanup

### 1. Check the Frontend UI
- Go to your Knowledge Base section
- Look for files with "FAILED" status
- These were previously stuck files

### 2. Retry Failed Files
- Click the "Retry Indexing" button for failed files
- The system will attempt to process them again
- Monitor the status changes

### 3. Restart Services (if needed)
If many files were stuck, consider restarting these services:

#### Kafka Consumer
```bash
# Stop the consumer service
# Restart the consumer service
```

#### Celery Workers
```bash
# Stop celery workers
# Restart celery workers
```

#### Full Application Restart
```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

## System Health Monitoring

### Check Processing Statistics
Monitor these metrics in your logs:
- Files processed per minute
- Success/failure rates
- Queue depths
- Memory usage

### Built-in Cleanup Process
Your system has an automatic cleanup that runs on startup:
- Location: `backend/python/app/services/kafka_consumer.py`
- Function: `cleanup_in_progress_documents()`
- Runs automatically when Kafka consumer starts

## Prevention Strategies

### 1. Resource Monitoring
- Monitor memory usage during file processing
- Set appropriate resource limits
- Scale workers based on load

### 2. Timeout Configuration
- Set processing timeouts for large files
- Implement retry mechanisms with exponential backoff
- Configure dead letter queues for failed messages

### 3. Health Checks
- Implement regular health checks for processing services
- Monitor queue depths and processing rates
- Set up alerts for stuck file conditions

### 4. Graceful Shutdowns
- Ensure services shut down gracefully
- Allow in-progress files to complete before shutdown
- Implement proper signal handling

## Troubleshooting Common Issues

### Issue: Script Can't Find Python
**Solution**: Ensure Python is installed and in PATH
```bash
# Check Python installation
python --version
# or
python3 --version
```

### Issue: Import Errors
**Solution**: Ensure you're in the correct directory and virtual environment
```bash
# Navigate to correct directory
cd backend/python

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Issue: Database Connection Errors
**Solution**: Check ArangoDB service status
```bash
# Check if ArangoDB is running
docker ps | grep arango

# Check database connectivity
# Verify configuration in app/config/
```

### Issue: Permission Errors
**Solution**: Run with appropriate permissions
```bash
# Linux/Mac
sudo python quick_cleanup.py

# Windows (Run PowerShell as Administrator)
```

## Advanced Debugging

### Check Kafka Consumer Status
```python
# In Python console
from app.services.kafka_consumer import KafkaConsumerManager
# Check consumer status and processed messages
```

### Monitor Processing Pipeline
```python
# Check indexing pipeline status
from app.modules.indexing.run import IndexingPipeline
# Monitor pipeline health
```

### Database Queries
```aql
// ArangoDB query to check file statuses
FOR doc IN records
  COLLECT status = doc.indexingStatus WITH COUNT INTO count
  RETURN { status: status, count: count }
```

## Getting Help

If the cleanup script doesn't resolve your issue:

1. **Check Logs**: Look for error messages in application logs
2. **System Resources**: Verify memory, disk space, and CPU usage
3. **Service Status**: Ensure all required services are running
4. **Configuration**: Verify database and Kafka configurations

## File Locations

- **Cleanup Scripts**: `backend/python/quick_cleanup.py`
- **Kafka Consumer**: `backend/python/app/services/kafka_consumer.py`
- **Processing Pipeline**: `backend/python/app/modules/indexing/run.py`
- **Status Constants**: `backend/python/app/config/utils/named_constants/arangodb_constants.py`

## Success Indicators

After running the cleanup, you should see:
- ✅ No files stuck in IN_PROGRESS state
- ✅ Previously stuck files now show as FAILED
- ✅ New files process normally
- ✅ Processing queue is moving
- ✅ System logs show normal operation

---

**Note**: This cleanup process is safe and only updates file statuses. It doesn't delete any files or data. Failed files can always be retried through the UI. 