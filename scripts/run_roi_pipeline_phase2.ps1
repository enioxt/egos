<#
.SYNOPSIS
    Orchestrates Phase-2 of the ATRiAN ROI pipeline:
      1. Ingest vendor cost CSVs
      2. Ingest SaaS provider incidents feeds
      3. Re-generate master incident dataset
      4. Run ROI simulation with default model
      5. Emit quick summary to console

.DESCRIPTION
    Wraps Python scripts so analysts can refresh the full dataset with one command.
    Assumes EGOS project root is the current directory.

.NOTES
    Author: Cascade (AI) – 2025-06-15
#>
param(
    [string]$VendorCsvDir = "C:\EGOS\data\raw\vendor_costs",
    [string]$SaasFeedDir   = "C:\EGOS\data\raw\saas_incidents",
    [string]$ModelPath     = "C:\EGOS\data\roi\default_roi_model.yaml",
    [string]$OutJson       = "C:\EGOS\data\roi\latest_roi.json"
)

Write-Host "==== ATRiAN ROI PIPELINE – Phase 2 ===="

# 1. Vendor cost ingestion
Write-Host "[1/5] Ingesting vendor costs CSVs..." -ForegroundColor Cyan
python scripts\ingest_vendor_costs_csv.py --raw-dir $VendorCsvDir || exit $LASTEXITCODE

# 2. SaaS incident ingestion
Write-Host "[2/5] Ingesting SaaS incident feeds..." -ForegroundColor Cyan
python scripts\ingest_saas_incidents.py --raw-dir $SaasFeedDir || exit $LASTEXITCODE

# 3. Prepare master incidents parquet
Write-Host "[3/5] Building master incidents parquet..." -ForegroundColor Cyan
python scripts\roi_prepare_data.py || exit $LASTEXITCODE

# 4. Run ROI simulation
Write-Host "[4/5] Running ROI simulation..." -ForegroundColor Cyan
python scripts\roi_simulate.py --model $ModelPath --out $OutJson || exit $LASTEXITCODE

# 5. Show summary
Write-Host "[5/5] ROI simulation complete. Summary:" -ForegroundColor Green
Get-Content -Path $OutJson | ConvertFrom-Json | Format-List
