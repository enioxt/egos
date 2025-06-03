# migrate_project_docs.ps1
# Script to restructure EGOS documentation folders
# Moves contents from docs/project_documentation/* to docs/*

$ErrorActionPreference = "Stop" # Stop on first error for script control, can be 'Continue'

$sourceBase = "C:\EGOS\docs\project_documentation"
$targetBase = "C:\EGOS\docs"

# Define moves: "SourceSubfolder" = "TargetSubfolder"
# Key = Subfolder name within $sourceBase
# Value = Subfolder name within $targetBase
$moves = @{
    "architecture" = "architecture"  # Target: $targetBase\architecture (New)
    "core"         = "reference"     # Target: $targetBase\reference (Merge)
    "governance"   = "governance"    # Target: $targetBase\governance (Merge)
    "guides"       = "guides"        # Target: $targetBase\guides (Merge)
    "process"      = "process"       # Target: $targetBase\process (New)
    "reference"    = "reference"     # Target: $targetBase\reference (Merge)
    "standards"    = "governance"    # Target: $targetBase\governance (Merge)
    "subsystems"   = "subsystems"    # Target: $targetBase\subsystems (Merge)
}

Write-Host "Starting documentation restructuring..."
Write-Host "Source Base: $sourceBase"
Write-Host "Target Base: $targetBase"

foreach ($sourceSubfolderKey in $moves.Keys) {
    $targetSubfolderName = $moves[$sourceSubfolderKey]
    $fullSourceSubfolderPath = Join-Path -Path $sourceBase -ChildPath $sourceSubfolderKey
    $fullTargetSubfolderPath = Join-Path -Path $targetBase -ChildPath $targetSubfolderName

    Write-Host "`nProcessing mapping: Contents of '$fullSourceSubfolderPath' ==> '$fullTargetSubfolderPath'"

    If (Test-Path $fullSourceSubfolderPath) {
        # Ensure the root target subfolder exists
        If (-not (Test-Path $fullTargetSubfolderPath)) {
            Write-Host "Creating target directory: '$fullTargetSubfolderPath'"
            New-Item -ItemType Directory -Path $fullTargetSubfolderPath -Force | Out-Null
        }

        # Move each item (files and sub-subfolders) from the source subfolder to the target subfolder
        Get-ChildItem -Path $fullSourceSubfolderPath | ForEach-Object {
            $itemToMove = $_            
            $destinationItemPath = Join-Path -Path $fullTargetSubfolderPath -ChildPath $itemToMove.Name
            
            Write-Host "  Attempting to move '$($itemToMove.FullName)' to '$destinationItemPath'..."
            If (Test-Path $destinationItemPath) {
                Write-Warning "  WARNING: Item '$($itemToMove.Name)' already exists at destination '$destinationItemPath'. Skipping this item."
            } Else {
                Try {
                    Move-Item -Path $itemToMove.FullName -Destination $destinationItemPath -ErrorAction Stop
                    Write-Host "  Successfully moved '$($itemToMove.FullName)'."
                } Catch {
                    Write-Error "  ERROR: Could not move '$($itemToMove.FullName)'. Error: $($_.Exception.Message)"
                }
            }
        }
        
        # Check if source subfolder is now empty and remove it
        If ((Get-ChildItem -Path $fullSourceSubfolderPath).Count -eq 0) {
            Write-Host "Source subfolder '$fullSourceSubfolderPath' is empty. Removing it."
            Remove-Item -Path $fullSourceSubfolderPath -Recurse -Force
        } Else {
            Write-Warning "WARNING: Source subfolder '$fullSourceSubfolderPath' is not empty after attempting moves. Please check manually."
        }

    } Else {
        Write-Host "Source subfolder '$fullSourceSubfolderPath' not found. Skipping."
    }
}

# Attempt to remove the base project_documentation folder if it's empty
If (Test-Path $sourceBase) {
    If ((Get-ChildItem -Path $sourceBase).Count -eq 0) {
        Write-Host "`nBase source folder '$sourceBase' is empty. Removing it."
        Remove-Item -Path $sourceBase -Recurse -Force
    } Else {
        Write-Warning "WARNING: Base source folder '$sourceBase' is not empty after all operations. Please check manually."
    }
} Else {
    Write-Host "`nBase source folder '$sourceBase' does not exist or was already removed."
}

Write-Host "`nDocumentation restructuring script finished."
Write-Host "--------------------------------------------------------------------"
Write-Host "IMPORTANT: Files have been moved. Now, you MUST run a script to"
Write-Host "           update all cross-references within the documentation"
Write-Host "           located under '$targetBase'."
Write-Host "--------------------------------------------------------------------"
