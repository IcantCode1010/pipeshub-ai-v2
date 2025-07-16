# PowerShell script to collect Docker container logs from the last 5 minutes
# Author: Generated for PipesHub AI project
# Usage: Run this script from PowerShell CLI in any directory

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Starting Docker logs collection..." -ForegroundColor Green

# Step 1: Create or clear the docker-logs folder in the current working directory
$logsFolder = Join-Path -Path (Get-Location) -ChildPath "docker-logs"

try {
    # Check if the folder exists
    if (Test-Path -Path $logsFolder) {
        Write-Host "Clearing existing docker-logs folder..." -ForegroundColor Yellow
        # Remove all files in the folder but keep the folder itself
        Get-ChildItem -Path $logsFolder -File | Remove-Item -Force
    } else {
        Write-Host "Creating docker-logs folder..." -ForegroundColor Yellow
        # Create the folder if it doesn't exist
        New-Item -Path $logsFolder -ItemType Directory -Force | Out-Null
    }
} catch {
    Write-Error "Failed to create/clear docker-logs folder: $($_.Exception.Message)"
    exit 1
}

# Step 2: Get list of all currently running Docker containers
Write-Host "Fetching list of running Docker containers..." -ForegroundColor Yellow

try {
    # Use docker ps to get running containers in a parseable format
    # Format: CONTAINER ID, NAMES (space-separated for easy parsing)
    $dockerPsOutput = docker ps --format "table {{.ID}}`t{{.Names}}" --no-trunc
    
    # Check if docker command was successful
    if ($LASTEXITCODE -ne 0) {
        throw "Docker ps command failed with exit code $LASTEXITCODE"
    }
    
    # Skip the header line and process container information
    $containerLines = $dockerPsOutput | Select-Object -Skip 1
    
    if (-not $containerLines -or $containerLines.Count -eq 0) {
        Write-Host "No running Docker containers found." -ForegroundColor Yellow
        Write-Host "Script completed successfully." -ForegroundColor Green
        exit 0
    }
    
    Write-Host "Found $($containerLines.Count) running container(s)" -ForegroundColor Green
    
} catch {
    Write-Error "Failed to get Docker container list: $($_.Exception.Message)"
    Write-Host "Make sure Docker is running and accessible from PowerShell." -ForegroundColor Red
    exit 1
}

# Step 3: Process each running container
foreach ($containerLine in $containerLines) {
    # Skip empty lines
    if ([string]::IsNullOrWhiteSpace($containerLine)) {
        continue
    }
    
    # Split the line by multiple spaces to get container ID and name
    # The format is: LONG_CONTAINER_ID   CONTAINER_NAME (separated by multiple spaces)
    $parts = $containerLine -split '\s{2,}' # Split on 2 or more consecutive spaces
    
    if ($parts.Count -ge 2) {
        $containerId = $parts[0].Trim()
        $containerName = $parts[1].Trim()
        
        Write-Host "Processing container: $containerName (ID: $containerId)" -ForegroundColor Cyan
        
        # Step 4: Fetch logs from the last 5 minutes for this container
        try {
            # Create the log file path
            $logFileName = "$containerName.log"
            $logFilePath = Join-Path -Path $logsFolder -ChildPath $logFileName
            
            Write-Host "  Fetching logs from last 5 minutes..." -ForegroundColor Gray
            
            # Use docker logs with --since 5m to get logs from last 5 minutes
            # Redirect both stdout and stderr to capture all output
            # Use the container ID for more reliable identification
            $dockerLogsCommand = "docker logs --since 5m $containerId"
            
            # Execute the command and capture both stdout and stderr
            $logOutput = Invoke-Expression $dockerLogsCommand 2>&1
            
            # Check if the docker logs command was successful
            if ($LASTEXITCODE -eq 0) {
                # Step 5: Save logs to file (overwrite existing file)
                if ($logOutput) {
                    # Convert the output to string and save to file
                    $logContent = $logOutput | Out-String
                    $logContent | Out-File -FilePath $logFilePath -Encoding UTF8 -Force
                    Write-Host "  Logs saved to: $logFileName" -ForegroundColor Green
                } else {
                    # Create empty file if no logs found
                    "" | Out-File -FilePath $logFilePath -Encoding UTF8 -Force
                    Write-Host "  No logs found for the last 5 minutes - empty file created" -ForegroundColor Yellow
                }
            } else {
                Write-Warning "  Failed to fetch logs for container $containerName (exit code: $LASTEXITCODE)"
                # Create a file with error information
                "Error: Failed to fetch logs for container $containerName at $(Get-Date)" | Out-File -FilePath $logFilePath -Encoding UTF8 -Force
            }
            
        } catch {
            Write-Warning "  Error processing container $containerName : $($_.Exception.Message)"
            # Create a file with error information
            try {
                $errorLogPath = Join-Path -Path $logsFolder -ChildPath "$containerName.log"
                "Error: $($_.Exception.Message) at $(Get-Date)" | Out-File -FilePath $errorLogPath -Encoding UTF8 -Force
            } catch {
                Write-Warning "  Could not create error log file for $containerName"
            }
        }
    } else {
        Write-Warning "Could not parse container information from line: $containerLine"
    }
}

# Step 6: Summary
Write-Host "`nDocker logs collection completed!" -ForegroundColor Green
Write-Host "Log files saved in: $logsFolder" -ForegroundColor Green

# List the created log files
$logFiles = Get-ChildItem -Path $logsFolder -Filter "*.log"
if ($logFiles) {
    Write-Host "`nCreated log files:" -ForegroundColor Yellow
    foreach ($file in $logFiles) {
        $fileSize = [math]::Round($file.Length / 1KB, 2)
        Write-Host "  $($file.Name) ($fileSize KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "No log files were created." -ForegroundColor Yellow
}

Write-Host "`nScript execution completed successfully." -ForegroundColor Green
