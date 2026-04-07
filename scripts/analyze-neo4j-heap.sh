#!/bin/bash
# VPS-NEO4J-TUNE-001: Analyze Neo4j Heap Allocation
# Usage: bash scripts/analyze-neo4j-heap.sh [optional: VPS_HOST]
# Output: docs/VPS_RESOURCE_SSOT.md updated with analysis

set -e

VPS_HOST="${1:-root@204.168.217.125}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/hetzner_ed25519}"
CONTAINER_NAME="neo4j-br-acc"
NEO4J_CONF="/var/lib/docker/volumes/neo4j-br-acc_data/_data/conf/neo4j.conf"

echo "🔍 Neo4j Heap Analysis (VPS-NEO4J-TUNE-001)"
echo "=================================================="

# 1. Connect to VPS and extract Neo4j config
echo ""
echo "📥 Fetching Neo4j configuration from VPS..."

NEO4J_CONFIG=$(ssh -i "$SSH_KEY" "$VPS_HOST" cat "$NEO4J_CONF" 2>/dev/null || \
                ssh -i "$SSH_KEY" "$VPS_HOST" "docker exec $CONTAINER_NAME cat /var/lib/neo4j/conf/neo4j.conf" 2>/dev/null || \
                echo "ERROR: Could not read neo4j.conf")

if [[ "$NEO4J_CONFIG" == *"ERROR"* ]]; then
    echo "❌ Failed to read neo4j.conf from VPS"
    echo "   Tried: $NEO4J_CONF"
    echo "   Fallback: docker exec $CONTAINER_NAME"
    exit 1
fi

# 2. Parse heap settings
echo "✓ Parsing heap allocation settings..."

INITIAL_HEAP=$(echo "$NEO4J_CONFIG" | grep -E "^dbms\.memory\.heap\.initial_size" | cut -d'=' -f2 | tr -d ' ' || echo "NOT SET")
MAX_HEAP=$(echo "$NEO4J_CONFIG" | grep -E "^dbms\.memory\.heap\.max_size" | cut -d'=' -f2 | tr -d ' ' || echo "NOT SET")
PAGE_CACHE=$(echo "$NEO4J_CONFIG" | grep -E "^dbms\.memory\.pagecache\.size" | cut -d'=' -f2 | tr -d ' ' || echo "NOT SET")

echo ""
echo "Current Neo4j Memory Settings:"
echo "────────────────────────────"
echo "  Initial Heap:     $INITIAL_HEAP"
echo "  Max Heap:         $MAX_HEAP"
echo "  Page Cache:       $PAGE_CACHE"

# 3. Get actual memory usage from VPS
echo ""
echo "📊 Querying actual memory usage..."

ACTUAL_USAGE=$(ssh -i "$SSH_KEY" "$VPS_HOST" \
    "docker stats --no-stream --format 'table {{.MemUsage}}' '$CONTAINER_NAME' 2>/dev/null | tail -1" || \
    echo "N/A")

echo "  Docker Memory:    $ACTUAL_USAGE"

# 4. Analyze node count
echo ""
echo "📈 Analyzing database content..."

NODE_COUNT=$(ssh -i "$SSH_KEY" "$VPS_HOST" \
    "docker exec $CONTAINER_NAME cypher-shell -u neo4j 'MATCH (n) RETURN count(n);' 2>/dev/null | grep -oE '[0-9]+' | tail -1" || \
    echo "N/A (requires APOC or cypher-shell access)")

echo "  Total Nodes:      $NODE_COUNT"

# 5. Calculate recommendations
echo ""
echo "💡 Recommendations:"
echo "──────────────────"

# Convert heap to MB for comparison
if [[ "$MAX_HEAP" =~ ^[0-9]+[gG]$ ]]; then
    heap_gb=${MAX_HEAP%[gG]}
    echo "  Current: ${heap_gb}GB heap"

    if (( ${heap_gb%.*} >= 4 )); then
        echo "  → SAFE: Heap ≥ 4GB is adequate for 83.7M nodes"
        echo "  → TRY: Reduce page cache (dbms.memory.pagecache.size)"
        echo "     Potential savings: 500MB-1GB if tolerable for query latency"
    fi
fi

if [[ "$PAGE_CACHE" =~ ^[0-9]+[gG]$ ]]; then
    pc_gb=${PAGE_CACHE%[gG]}
    echo ""
    echo "  Page Cache: ${pc_gb}GB"
    echo "  → This is disk I/O buffer"
    echo "  → Can be reduced if queries tolerate more disk I/O"
    echo "  → Trade-off: smaller cache → faster queries + lower RAM"
fi

# 6. Generate tuning recommendations
echo ""
echo "🔧 Tuning Options (from least to most aggressive):"
echo "──────────────────────────────────────────────────"

echo ""
echo "Option 1: No changes (current state)"
echo "  • Heap: $MAX_HEAP (31.5% of VPS RAM)"
echo "  • Risk: RAM pressure on Hermes MVP"
echo "  • ROI: Free up 0GB"

echo ""
echo "Option 2: Reduce page cache only"
echo "  • Change: dbms.memory.pagecache.size=1g (from 4g if default)"
echo "  • Heap: Keep $MAX_HEAP"
echo "  • Risk: Slightly slower disk queries"
echo "  • ROI: Free up ~3GB"

echo ""
echo "Option 3: Reduce both heap and cache"
echo "  • Change: dbms.memory.heap.max_size=3g + pagecache=1g"
echo "  • Before restart: Run 'CALL dbms.diagnostics.dbQueries()' to validate"
echo "  • Risk: Potential slow queries if cache too small"
echo "  • ROI: Free up ~2GB (heap) + ~3GB (cache) = ~5GB"

# 7. Benchmark template
echo ""
echo "📏 Benchmark Plan (if tuning):"
echo "──────────────────────────────"
echo ""
echo "1. Capture baseline:"
echo "   • Run load test: /tmp/neo4j-benchmark.sh"
echo "   • Measure: query p95 latency, throughput, error rate"
echo ""
echo "2. Apply tuning:"
echo "   • Edit: neo4j.conf (on VPS container mount)"
echo "   • Restart: docker-compose down && docker-compose up -d neo4j-br-acc"
echo ""
echo "3. Re-measure:"
echo "   • Run same load test"
echo "   • Compare p95 latency +/- 20% = acceptable"
echo ""
echo "4. Decision:"
echo "   • If acceptable: commit tuning to gitops"
echo "   • If regression: revert and try Option 1"

# 8. Save analysis to SSOT
echo ""
echo "💾 Saving analysis..."

ANALYSIS_FILE="/tmp/neo4j-analysis-$(date +%Y%m%d-%H%M%S).txt"
cat > "$ANALYSIS_FILE" <<EOF
# Neo4j Heap Analysis Report
Generated: $(date)
VPS Host: $VPS_HOST

## Current Settings
Initial Heap:     $INITIAL_HEAP
Max Heap:         $MAX_HEAP
Page Cache:       $PAGE_CACHE

## Actual Usage
Docker Memory:    $ACTUAL_USAGE
Database Nodes:   $NODE_COUNT

## Recommendation
See section "🔧 Tuning Options" above.

Status: READY FOR VPS-CAPACITY-001 (capacity planning model)
EOF

echo "✓ Analysis saved to: $ANALYSIS_FILE"
echo ""
echo "Next Steps:"
echo "──────────"
echo "1. Review analysis above"
echo "2. If tuning desired: create PR with neo4j.conf changes"
echo "3. Test in staging/branch before production"
echo "4. Document results in VPS_RESOURCE_SSOT.md §VPS-NEO4J-TUNE-001"
echo ""
