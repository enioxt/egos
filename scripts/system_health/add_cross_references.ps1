# Add Cross References to Recently Created Files
# Author: EGOS Development Team
# Date: 2025-05-18
# Description: Adds proper cross-references to recently created roadmap hierarchy files

$files = @(
    "C:\EGOS\docs\audits\index.md",
    "C:\EGOS\docs\governance\roadmap_hierarchy.md",
    "C:\EGOS\docs\governance\roadmap_standardization.md",
    "C:\EGOS\docs\templates\roadmap_template.md",
    "C:\EGOS\docs\templates\main_roadmap_template.md",
    "C:\EGOS\docs\reference\roadmap_hierarchy_implementation.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Processing $file..."
        
        # Read file content
        $content = Get-Content -Path $file -Raw
        
        # Check if file already has cross-references
        if ($content -match "## Cross References") {
            Write-Host "File already has cross-references. Skipping."
            continue
        }
        
        # Extract metadata section
        $metadataMatch = [regex]::Match($content, "(?s)^---\n(.*?)\n---\n")
        if (-not $metadataMatch.Success) {
            Write-Host "No metadata section found. Skipping."
            continue
        }
        
        $metadata = $metadataMatch.Value
        $bodyContent = $content.Substring($metadataMatch.Length)
        
        # Create cross-references section based on file path
        $crossReferences = "## Cross References\n\n"
        
        # Add standard cross-references
        $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        
        # Add specific cross-references based on file type
        if ($file -like "*roadmap_hierarchy*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        elseif ($file -like "*roadmap_standardization*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        elseif ($file -like "*roadmap_template*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        elseif ($file -like "*main_roadmap_template*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        elseif ($file -like "*roadmap_hierarchy_implementation*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        elseif ($file -like "*audits\index*") {
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
            $crossReferences += "- <!-- TO_BE_REPLACED -->\n"
        }
        
        $crossReferences += "\n"
        
        # Insert cross-references after metadata
        $newContent = $metadata + $crossReferences + $bodyContent
        
        # Write updated content back to file
        Set-Content -Path $file -Value $newContent -Encoding UTF8
        
        Write-Host "Added cross-references to $file"
    }
    else {
        Write-Host "File not found: $file"
    }
}

Write-Host "Cross-reference addition completed."