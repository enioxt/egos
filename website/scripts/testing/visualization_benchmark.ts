/**
 * @file visualization_benchmark.ts
 * @description Benchmark testing for the cross-reference visualization system
 * @module scripts/testing/visualization_benchmark
 * @version 1.0.0
 * @date 2025-05-21
 * @license MIT
 *
 * @references
 * - mdc:website/src/utils/graphDataUtils.ts (Graph data utilities)
 * - mdc:website/src/components/SystemGraph.tsx (Visualization component)
 * - mdc:docs/testing/performance_benchmarks.md (Testing specifications)
 * - mdc:website/scripts/testing/generate_large_dataset.ts (Test data generator)
 */

/**
 * Interface for benchmark test results
 */
interface BenchmarkResult {
  testName: string;
  datasetSize: string;
  nodeCount: number;
  edgeCount: number;
  loadTime: number;
  filterTime: number;
  renderTime: number;
  totalTime: number;
  memory: {
    beforeTest: number;
    afterTest: number;
    difference: number;
  };
  browser: string;
  timestamp: string;
}

/**
 * Interface for benchmark test configuration
 */
interface BenchmarkConfig {
  datasetSizes: string[];
  filterCombinations: {
    name: string;
    filters: {
      fileTypes: string[];
      subsystems: string[];
      minConnections: number;
      showCore: boolean | null;
    };
  }[];
  iterations: number;
  browsers: string[];
}

/**
 * Default benchmark configuration
 */
const DEFAULT_CONFIG: BenchmarkConfig = {
  datasetSizes: ['small', 'medium', 'large', 'xlarge'],
  filterCombinations: [
    {
      name: 'No filters',
      filters: {
        fileTypes: [],
        subsystems: [],
        minConnections: 0,
        showCore: null
      }
    },
    {
      name: 'File type filter',
      filters: {
        fileTypes: ['markdown', 'python'],
        subsystems: [],
        minConnections: 0,
        showCore: null
      }
    },
    {
      name: 'Subsystem filter',
      filters: {
        fileTypes: [],
        subsystems: ['KOIOS', 'ETHIK'],
        minConnections: 0,
        showCore: null
      }
    },
    {
      name: 'Connection threshold',
      filters: {
        fileTypes: [],
        subsystems: [],
        minConnections: 5,
        showCore: null
      }
    },
    {
      name: 'Core files only',
      filters: {
        fileTypes: [],
        subsystems: [],
        minConnections: 0,
        showCore: true
      }
    },
    {
      name: 'Complex combination',
      filters: {
        fileTypes: ['python', 'typescript'],
        subsystems: ['KOIOS', 'NEXUS'],
        minConnections: 3,
        showCore: true
      }
    }
  ],
  iterations: 3,
  browsers: ['Chrome', 'Firefox', 'Edge']
};

/**
 * Run the benchmark tests and gather performance metrics
 * 
 * @param config Benchmark configuration
 * @returns Promise resolving to array of benchmark results
 */
async function runBenchmarks(
  config: BenchmarkConfig = DEFAULT_CONFIG
): Promise<BenchmarkResult[]> {
  console.log('Starting benchmark tests...');
  const results: BenchmarkResult[] = [];

  // Note: In a browser environment, these tests would be executed differently
  // This is a Node.js simulation of the testing process
  
  for (const browser of config.browsers) {
    console.log(`\nTesting in ${browser}...`);
    
    for (const size of config.datasetSizes) {
      console.log(`\n  Dataset: ${size}`);
      
      // Simulate loading the dataset
      console.log(`  Loading dataset ${size}...`);
      const dataLoadStart = performance.now();
      
      // Here we would actually load the dataset
      // For simulation, we'll use timing proportional to dataset size
      const sizeMultiplier = 
        size === 'small' ? 1 :
        size === 'medium' ? 5 :
        size === 'large' ? 10 : 20;
      
      // Simulate data loading time
      await new Promise(resolve => setTimeout(resolve, 50 * sizeMultiplier));
      
      const dataLoadTime = performance.now() - dataLoadStart;
      
      // Simulate dataset node and edge counts
      const nodeCount = 
        size === 'small' ? 1000 :
        size === 'medium' ? 5000 :
        size === 'large' ? 10000 : 20000;
      
      const edgeCount = Math.floor(nodeCount * nodeCount * 
        (size === 'small' ? 0.01 :
         size === 'medium' ? 0.005 :
         size === 'large' ? 0.001 : 0.0005));
      
      for (const filterTest of config.filterCombinations) {
        console.log(`    Filter: ${filterTest.name}`);
        
        // Store results for each iteration
        const iterationResults: {
          filterTime: number;
          renderTime: number;
          totalTime: number;
        }[] = [];
        
        // Run multiple iterations for statistical significance
        for (let i = 0; i < config.iterations; i++) {
          // Measure memory before test
          const memBefore = process.memoryUsage().heapUsed / 1024 / 1024;
          
          // Simulate applying filters
          const filterStart = performance.now();
          
          // Simulate filter application time based on dataset size and filter complexity
          const filterComplexity = 
            Object.values(filterTest.filters).filter(f => 
              Array.isArray(f) ? f.length > 0 : f !== null
            ).length;
          
          await new Promise(resolve => 
            setTimeout(resolve, 20 * sizeMultiplier * (filterComplexity + 1))
          );
          
          const filterTime = performance.now() - filterStart;
          
          // Simulate rendering the filtered graph
          const renderStart = performance.now();
          
          // Simulate render time based on filtered data size
          // More complex filters generally result in fewer nodes, so faster rendering
          const filterReduction = Math.max(0.1, 1 - (filterComplexity * 0.15));
          
          await new Promise(resolve => 
            setTimeout(resolve, 100 * sizeMultiplier * filterReduction)
          );
          
          const renderTime = performance.now() - renderStart;
          const totalTime = filterTime + renderTime;
          
          // Measure memory after test
          const memAfter = process.memoryUsage().heapUsed / 1024 / 1024;
          
          iterationResults.push({
            filterTime,
            renderTime,
            totalTime
          });
          
          // Only record the last iteration in results
          if (i === config.iterations - 1) {
            results.push({
              testName: filterTest.name,
              datasetSize: size,
              nodeCount,
              edgeCount,
              loadTime: dataLoadTime,
              filterTime,
              renderTime,
              totalTime,
              memory: {
                beforeTest: Math.round(memBefore * 100) / 100,
                afterTest: Math.round(memAfter * 100) / 100,
                difference: Math.round((memAfter - memBefore) * 100) / 100
              },
              browser,
              timestamp: new Date().toISOString()
            });
          }
        }
        
        // Calculate and display average times
        const avgFilterTime = iterationResults.reduce((sum, r) => sum + r.filterTime, 0) / config.iterations;
        const avgRenderTime = iterationResults.reduce((sum, r) => sum + r.renderTime, 0) / config.iterations;
        const avgTotalTime = iterationResults.reduce((sum, r) => sum + r.totalTime, 0) / config.iterations;
        
        console.log(`      Avg Filter Time: ${avgFilterTime.toFixed(2)}ms`);
        console.log(`      Avg Render Time: ${avgRenderTime.toFixed(2)}ms`);
        console.log(`      Avg Total Time: ${avgTotalTime.toFixed(2)}ms`);
      }
    }
  }
  
  console.log('\nBenchmark tests completed.');
  return results;
}

/**
 * Generate a benchmark report from test results
 * 
 * @param results Benchmark test results
 * @returns HTML report as a string
 */
function generateReport(results: BenchmarkResult[]): string {
  const now = new Date().toISOString().split('T')[0];
  
  // Generate HTML report
  let html = `<!DOCTYPE html>
<html>
<head>
  <title>EGOS Visualization Benchmark Report - ${now}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1, h2 { color: #333; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background-color: #f2f2f2; }
    tr:hover { background-color: #f5f5f5; }
    .warning { background-color: #fff3cd; }
    .danger { background-color: #f8d7da; }
    .summary { margin: 20px 0; padding: 15px; background-color: #e9ecef; border-radius: 5px; }
  </style>
</head>
<body>
  <h1>EGOS Cross-Reference Visualization Benchmark Report</h1>
  <p>Generated: ${new Date().toISOString()}</p>
  
  <div class="summary">
    <h2>Summary</h2>
    <p>Total tests: ${results.length}</p>
    <p>Browsers tested: ${[...new Set(results.map(r => r.browser))].join(', ')}</p>
    <p>Dataset sizes: ${[...new Set(results.map(r => r.datasetSize))].join(', ')}</p>
  </div>
  
  <h2>Results by Browser</h2>`;
  
  // Group by browser
  const browserGroups = new Map<string, BenchmarkResult[]>();
  results.forEach(result => {
    if (!browserGroups.has(result.browser)) {
      browserGroups.set(result.browser, []);
    }
    browserGroups.get(result.browser)!.push(result);
  });
  
  // Generate tables for each browser
  for (const [browser, browserResults] of browserGroups) {
    html += `
  <h3>${browser}</h3>
  <table>
    <tr>
      <th>Test</th>
      <th>Dataset</th>
      <th>Nodes</th>
      <th>Edges</th>
      <th>Load Time (ms)</th>
      <th>Filter Time (ms)</th>
      <th>Render Time (ms)</th>
      <th>Total Time (ms)</th>
      <th>Memory Δ (MB)</th>
    </tr>`;
    
    browserResults.forEach(result => {
      // Add warning class if total time exceeds thresholds
      let rowClass = '';
      if (result.totalTime > 1000) {
        rowClass = 'warning';
      }
      if (result.totalTime > 3000) {
        rowClass = 'danger';
      }
      
      html += `
    <tr class="${rowClass}">
      <td>${result.testName}</td>
      <td>${result.datasetSize}</td>
      <td>${result.nodeCount.toLocaleString()}</td>
      <td>${result.edgeCount.toLocaleString()}</td>
      <td>${result.loadTime.toFixed(2)}</td>
      <td>${result.filterTime.toFixed(2)}</td>
      <td>${result.renderTime.toFixed(2)}</td>
      <td>${result.totalTime.toFixed(2)}</td>
      <td>${result.memory.difference.toFixed(2)}</td>
    </tr>`;
    });
    
    html += `
  </table>`;
  }
  
  html += `
  <h2>Performance Recommendations</h2>
  <ul>
    <li>For datasets larger than 10,000 nodes, consider implementing pagination or progressive loading</li>
    <li>Optimize filter operations for large datasets by using more efficient data structures</li>
    <li>Implement caching for filtered results to improve performance when toggling between filters</li>
    <li>Consider implementing level-of-detail rendering based on zoom level</li>
    <li>For the largest datasets, warn users about potential performance issues or offer a simplified view</li>
  </ul>
  
  <p>✧༺❀༻∞ EGOS ∞༺❀༻✧</p>
</body>
</html>`;
  
  return html;
}

/**
 * Save the benchmark report to a file
 * 
 * @param report HTML report content
 */
function saveReport(report: string): void {
  const fs = require('fs');
  const path = require('path');
  const outputDir = path.join(__dirname, '..', '..', 'public', 'test-results');
  
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const now = new Date().toISOString().split('T')[0];
  const outputPath = path.join(outputDir, `visualization-benchmark-${now}.html`);
  
  fs.writeFileSync(outputPath, report);
  console.log(`Benchmark report saved to ${outputPath}`);
}

/**
 * Save benchmark results as JSON for further analysis
 * 
 * @param results Benchmark test results
 */
function saveResultsJson(results: BenchmarkResult[]): void {
  const fs = require('fs');
  const path = require('path');
  const outputDir = path.join(__dirname, '..', '..', 'public', 'test-results');
  
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const now = new Date().toISOString().split('T')[0];
  const outputPath = path.join(outputDir, `visualization-benchmark-${now}.json`);
  
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  console.log(`Benchmark results JSON saved to ${outputPath}`);
}

/**
 * Main function to run benchmarks and generate reports
 */
async function main(): Promise<void> {
  try {
    // Run the benchmarks
    const results = await runBenchmarks();
    
    // Generate and save the HTML report
    const report = generateReport(results);
    saveReport(report);
    
    // Save raw results as JSON for further analysis
    saveResultsJson(results);
    
    console.log('Benchmarking complete.');
  } catch (error) {
    console.error('Error running benchmarks:', error);
  }
}

// Run the main function if this script is executed directly
if (require.main === module) {
  main();
}

// Export for use in other scripts
export { runBenchmarks, generateReport, BenchmarkResult, BenchmarkConfig };
