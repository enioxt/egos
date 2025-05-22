# EGOS Comprehensive Website Structure Fix
# Implements multiple EGOS principles: Conscious Modularity, Integrated Ethics, Systemic Cartography
# <!-- TO_BE_REPLACED -->MEMORY[user_global], MEMORY[7e443f56...], MEMORY[d18c5768...]

<#
@metadata
@title EGOS Website Structure Fix
@description Comprehensive script to fix Next.js structural issues and prepare for future development
@author EgosArchitect
@version 1.0.0
@date 2025-04-24
@status ⚡ Active
@references
- `mdc:website/next.config.js`
- `mdc:website/src/app/page.tsx`
- `mdc:website/src/components/HomeContent.tsx`
#>

Write-Output "=== EGOS Website Structure Fix Tool ==="
Write-Output "Applying comprehensive structure improvements..."

# 1. Create a clean basic globals.css file (resolving Tailwind issues)
Write-Output "Creating clean globals.css file..."
@"
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Root theme variables (light & dark mode support) */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;

  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;

  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;

  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;

  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;

  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;

  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;

  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;

  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;

  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;

  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;

  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;

  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;

  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;

  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;

  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;

  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;

  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}

* {
  @apply border-border;
}

body {
  @apply bg-background text-foreground;
}

html {
  height: 100%;
  scroll-behavior: smooth;
}
"@ | Out-File -FilePath "src\app\globals.css" -Encoding utf8 -Force

# 2. Clear any remaining .old, .bak, .new files
Write-Output "Cleaning up temporary files..."
Get-ChildItem -Path "src" -Recurse -Include "*.old","*.bak","*.new" | ForEach-Object {
    Write-Output "Removing $($_.FullName)"
    Remove-Item -Path $_.FullName -Force
}

# 3. Move all files from components_old to src/components if they don't exist
if (Test-Path "components_old") {
    Write-Output "Moving any missing components from components_old to src\components..."
    Get-ChildItem -Path "components_old" -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($_.FullName.IndexOf("components_old") + "components_old".Length)
        $targetPath = Join-Path "src\components" $relativePath
        
        # Ensure target directory exists
        $targetDir = Split-Path -Path $targetPath -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
        }
        
        if (-not (Test-Path $targetPath)) {
            Write-Output "Copying $relativePath to src\components$relativePath"
            Copy-Item -Path $_.FullName -Destination $targetPath -Force
        }
    }
}

# 4. Ensure src/app/page.tsx and HomeContent.tsx references are correct
Write-Output "Validating critical component references..."
if (Test-Path "src\components\HomeContent.tsx") {
    Write-Output "HomeContent.tsx exists, ensuring imports are correct..."
    $homeContentPath = "src\components\HomeContent.tsx"
    $pageContent = Get-Content -Path "src\app\page.tsx" -Raw
    
    # Check if HomeContent import is correct in page.tsx
    if ($pageContent -match "import \{ HomeContent \} from '@/components/HomeContent'") {
        Write-Output "  • HomeContent import in page.tsx is correct."
    } else {
        Write-Output "  • Fixing HomeContent import in page.tsx..."
        $updatedPageContent = $pageContent -replace "import \{.*HomeContent.*\} from .*", "import { HomeContent } from '@/components/HomeContent';"
        Set-Content -Path "src\app\page.tsx" -Value $updatedPageContent -Force
    }
}

# 5. Remove old locale directory completely
if (Test-Path "src\app\en.old") {
    Write-Output "Removing old locale directory..."
    Remove-Item -Path "src\app\en.old" -Recurse -Force
}

if (Test-Path "src\app\en") {
    Write-Output "Moving any useful files from src\app\en to appropriate locations..."
    # For RoadmapSection, move to content
    if (Test-Path "src\app\en\RoadmapSection.tsx") {
        $targetDir = "src\components\content"
        if (-not (Test-Path $targetDir)) {
            New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
        }
        Copy-Item -Path "src\app\en\RoadmapSection.tsx" -Destination "$targetDir\RoadmapSection.tsx" -Force
    }
    
    # Then remove en directory
    Write-Output "Removing src\app\en directory..."
    Rename-Item -Path "src\app\en" -NewName "en.old" -Force
}

# 6. Create a simple components/ui directory if it doesn't exist
if (-not (Test-Path "src\components\ui")) {
    Write-Output "Creating basic UI components directory..."
    New-Item -Path "src\components\ui" -ItemType Directory -Force | Out-Null
}

# 7. Remove components.old directory to prevent confusion
if (Test-Path "components.old") {
    Write-Output "Removing components.old directory..."
    Remove-Item -Path "components.old" -Recurse -Force
}

if (Test-Path "components") {
    Write-Output "Renaming components to components.backup..."
    if (Test-Path "components.backup") {
        Remove-Item -Path "components.backup" -Recurse -Force
    }
    Rename-Item -Path "components" -NewName "components.backup" -Force
}

Write-Output "=== Structure Fix Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved."
