# Run performance optimizations manually
# Can be scheduled via WARP or run directly

param(
    [switch]$DatabaseOnly = $false,
    [switch]$CacheOnly = $false,
    [switch]$SearchOnly = $false,
    [switch]$All = $true
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Performance Optimizations..." -ForegroundColor Cyan
Write-Host ""

if ($DatabaseOnly -or $All) {
    Write-Host "📊 Step 1: Database Index Optimization..." -ForegroundColor Yellow
    
    Write-Host "  Analyzing table statistics..." -ForegroundColor White
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c "ANALYZE anonymous_users, llc_profiles, job_postings, capability_assessments, matches;" 2>&1 | Out-Null
    
    Write-Host "  Checking for missing indexes..." -ForegroundColor White
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c @"
    SELECT
      schemaname,
      tablename,
      attname,
      n_distinct
    FROM pg_stats
    WHERE schemaname = 'public'
      AND n_distinct > 100
    ORDER BY n_distinct DESC
    LIMIT 10;
"@ | Select-Object -Last 15
    
    Write-Host "  Reindexing critical tables..." -ForegroundColor White
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c "REINDEX TABLE CONCURRENTLY anonymous_users;" 2>&1 | Out-Null
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c "REINDEX TABLE CONCURRENTLY llc_profiles;" 2>&1 | Out-Null
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c "REINDEX TABLE CONCURRENTLY job_postings;" 2>&1 | Out-Null
    
    Write-Host "  ✅ Database optimization complete" -ForegroundColor Green
    Write-Host ""
}

if ($CacheOnly -or $All) {
    Write-Host "💾 Step 2: Redis Cache Optimization..." -ForegroundColor Yellow
    
    Write-Host "  Checking cache statistics..." -ForegroundColor White
    docker compose exec -T redis redis-cli INFO stats | Select-String -Pattern "keyspace_hits|keyspace_misses" | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
    
    Write-Host "  Optimizing memory policy..." -ForegroundColor White
    docker compose exec -T redis redis-cli CONFIG SET maxmemory-policy allkeys-lru 2>&1 | Out-Null
    
    Write-Host "  ✅ Cache optimization complete" -ForegroundColor Green
    Write-Host ""
}

if ($SearchOnly -or $All) {
    Write-Host "🔍 Step 3: Elasticsearch Index Optimization..." -ForegroundColor Yellow
    
    Write-Host "  Checking cluster health..." -ForegroundColor White
    $health = curl -s http://localhost:9200/_cluster/health 2>&1
    Write-Host "    $health" -ForegroundColor White
    
    Write-Host "  Refreshing indexes..." -ForegroundColor White
    curl -X POST "http://localhost:9200/_refresh" 2>&1 | Out-Null
    
    Write-Host "  ✅ Search optimization complete" -ForegroundColor Green
    Write-Host ""
}

if ($All) {
    Write-Host "📈 Step 4: Performance Metrics..." -ForegroundColor Yellow
    
    Write-Host "  Database size:" -ForegroundColor White
    docker compose exec -T postgres psql -U jobfinder -d jobfinder -c "SELECT pg_size_pretty(pg_database_size('jobfinder'));" 2>&1 | Select-Object -Last 3
    
    Write-Host "  Cache hit rate:" -ForegroundColor White
    $hits = docker compose exec -T redis redis-cli INFO stats | Select-String -Pattern "keyspace_hits:(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    $misses = docker compose exec -T redis redis-cli INFO stats | Select-String -Pattern "keyspace_misses:(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    if ($hits -and $misses) {
        $total = [int]$hits + [int]$misses
        if ($total -gt 0) {
            $hitRate = ([int]$hits / $total * 100)
            Write-Host "    Hit Rate: $([math]::Round($hitRate, 2))%" -ForegroundColor White
        }
    }
    
    Write-Host ""
}

Write-Host "✅ Performance optimizations completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "  • Monitor performance metrics" -ForegroundColor White
Write-Host "  • Review slow query logs" -ForegroundColor White
Write-Host "  • Check cache hit rates" -ForegroundColor White

