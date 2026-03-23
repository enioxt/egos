#!/usr/bin/env node

/**
 * API Quota Diagnostic Tool
 * 
 * Tests each API/model to discover:
 * - What actually works
 * - Remaining quotas
 * - Rate limits
 * - Real capabilities vs theory
 * 
 * Usage:
 *   node diagnose-quotas.js [provider]
 *   
 * Providers:
 *   openrouter    - Test OpenRouter models
 *   alibaba       - Test Alibaba DashScope
 *   groq          - Test Groq
 *   cohere        - Test Cohere
 *   all           - Test all configured providers
 */

const https = require('https');
const http = require('http');
const fs = require('fs');

// Configuration for each provider
const PROVIDERS = {
  openrouter: {
    baseUrl: 'api.openrouter.ai',
    port: 443,
    protocol: 'https',
    apiKey: process.env.OPENROUTER_API_KEY,
    endpoint: '/api/v1/chat/completions',
    models: [
      'google/gemini-2.0-flash:free',
      'meta-llama/llama-3.3-70b-instruct:free',
      'mistralai/mistral-7b-instruct:free',
      'google/gemini-2.0-flash-001',
      'openai/gpt-4o-mini',
      'deepseek/deepseek-chat-v3-0324',
      'anthropic/claude-opus-4.6',
      'anthropic/claude-sonnet-4-20250514',
      'anthropic/claude-3.5-haiku-20241022',
    ],
    testPayload: (model) => ({
      model: model,
      messages: [
        {
          role: 'user',
          content:
            'Say only "ALIVE" and nothing else. No explanation, just the word ALIVE.',
        },
      ],
      max_tokens: 10,
    }),
    headers: (apiKey) => ({
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': 'http://localhost:3000',
      'X-Title': 'EGOS Quota Diagnostic',
      'Content-Type': 'application/json',
    }),
  },
  alibaba: {
    baseUrl: 'dashscope-intl.aliyuncs.com',
    port: 443,
    protocol: 'https',
    apiKey: process.env.ALIBABA_DASHSCOPE_API_KEY,
    endpoint: '/compatible-mode/v1/chat/completions',
    models: [
      'qwen-turbo',
      'qwen-plus',
      'qwen-max',
      'qwen-flash',
      'qwen3-coder-plus',
    ],
    testPayload: (model) => ({
      model: model,
      messages: [
        {
          role: 'user',
          content: 'Say only "ALIVE" and nothing else.',
        },
      ],
      max_tokens: 10,
    }),
    headers: (apiKey) => ({
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    }),
  },
  groq: {
    baseUrl: 'api.groq.com',
    port: 443,
    protocol: 'https',
    apiKey: process.env.GROQ_API_KEY,
    endpoint: '/openai/v1/chat/completions',
    models: [
      'mixtral-8x7b-32768',
      'llama-2-70b-4096',
      'gemma-7b-it',
    ],
    testPayload: (model) => ({
      model: model,
      messages: [
        {
          role: 'user',
          content: 'Say only "ALIVE" and nothing else.',
        },
      ],
      max_tokens: 10,
    }),
    headers: (apiKey) => ({
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    }),
  },
};

class QuotaDiagnostic {
  constructor() {
    this.results = [];
    this.timestamp = new Date().toISOString();
  }

  /**
   * Make HTTP/HTTPS request
   */
  async request(protocol, host, port, path, method, headers, body) {
    return new Promise((resolve, reject) => {
      const client = protocol === 'https' ? https : http;

      const options = {
        hostname: host,
        port: port,
        path: path,
        method: method,
        headers: headers,
        timeout: 10000,
      };

      const req = client.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const parsed = JSON.parse(data);
            resolve({
              status: res.statusCode,
              statusText: res.statusMessage,
              headers: res.headers,
              body: parsed,
              data: data,
            });
          } catch (e) {
            resolve({
              status: res.statusCode,
              statusText: res.statusMessage,
              headers: res.headers,
              body: null,
              data: data,
            });
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      if (body) {
        req.write(JSON.stringify(body));
      }

      req.end();
    });
  }

  /**
   * Test a single model
   */
  async testModel(provider, providerConfig, model) {
    const startTime = Date.now();

    try {
      if (!providerConfig.apiKey) {
        return {
          provider: provider,
          model: model,
          status: 'SKIPPED',
          reason: 'No API key configured',
          duration: 0,
        };
      }

      const response = await this.request(
        providerConfig.protocol,
        providerConfig.baseUrl,
        providerConfig.port,
        providerConfig.endpoint,
        'POST',
        providerConfig.headers(providerConfig.apiKey),
        providerConfig.testPayload(model),
      );

      const duration = Date.now() - startTime;

      if (response.status === 200) {
        const content = response.body?.choices?.[0]?.message?.content || '';
        return {
          provider: provider,
          model: model,
          status: 'WORKS',
          duration: duration,
          latency: `${duration}ms`,
          inputTokens: response.body?.usage?.prompt_tokens || 0,
          outputTokens: response.body?.usage?.completion_tokens || 0,
          response: content.substring(0, 50),
          error: null,
        };
      } else if (response.status === 401) {
        return {
          provider: provider,
          model: model,
          status: 'AUTH_FAILED',
          duration: duration,
          reason: 'Invalid API key',
          httpStatus: response.status,
          error: response.body?.error?.message || 'Unauthorized',
        };
      } else if (response.status === 429) {
        return {
          provider: provider,
          model: model,
          status: 'RATE_LIMITED',
          duration: duration,
          reason: 'Rate limit exceeded',
          httpStatus: response.status,
          error: response.body?.error?.message || 'Too many requests',
        };
      } else if (response.status === 400) {
        return {
          provider: provider,
          model: model,
          status: 'BAD_REQUEST',
          duration: duration,
          httpStatus: response.status,
          error: response.body?.error?.message || 'Bad request',
        };
      } else {
        return {
          provider: provider,
          model: model,
          status: `ERROR_${response.status}`,
          duration: duration,
          httpStatus: response.status,
          error: response.body?.error?.message || response.statusText,
        };
      }
    } catch (error) {
      return {
        provider: provider,
        model: model,
        status: 'FAILED',
        duration: Date.now() - startTime,
        reason: 'Connection error',
        error: error.message,
      };
    }
  }

  /**
   * Test all models in a provider
   */
  async testProvider(provider) {
    const config = PROVIDERS[provider];

    if (!config) {
      console.error(`❌ Unknown provider: ${provider}`);
      return;
    }

    console.log(`\n🧪 Testing ${provider.toUpperCase()}...\n`);

    const tests = config.models.map((model) =>
      this.testModel(provider, config, model),
    );

    const results = await Promise.all(tests);
    this.results.push(...results);

    return results;
  }

  /**
   * Display results
   */
  displayResults(results) {
    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║                    QUOTA DIAGNOSTIC RESULTS                    ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

    const working = results.filter((r) => r.status === 'WORKS');
    const failed = results.filter((r) => r.status !== 'WORKS');

    if (working.length > 0) {
      console.log('✅ WORKING MODELS:\n');
      console.log(
        'Provider'.padEnd(15) +
          'Model'.padEnd(40) +
          'Latency'.padEnd(12) +
          'Tokens',
      );
      console.log('─'.repeat(70));

      working.forEach((r) => {
        const model = (r.model || '').substring(0, 38).padEnd(40);
        const latency = (r.latency || '').padEnd(12);
        const tokens = `${r.inputTokens}/${r.outputTokens}`;
        console.log(
          r.provider.padEnd(15) + model + latency + tokens,
        );
      });
    }

    if (failed.length > 0) {
      console.log('\n\n❌ NOT WORKING:\n');
      console.log('Provider'.padEnd(15) + 'Model'.padEnd(40) + 'Issue');
      console.log('─'.repeat(70));

      failed.forEach((r) => {
        const model = (r.model || '').substring(0, 38).padEnd(40);
        const issue = r.status;
        console.log(r.provider.padEnd(15) + model + issue);
      });
    }

    console.log('\n\n📊 SUMMARY:\n');
    console.log(`Total tested: ${results.length}`);
    console.log(`Working: ${working.length}`);
    console.log(`Failed: ${failed.length}`);

    if (working.length > 0) {
      const avgLatency =
        working.reduce((sum, r) => sum + r.duration, 0) / working.length;
      console.log(`Average latency: ${Math.round(avgLatency)}ms`);
    }
  }

  /**
   * Save results to JSON
   */
  saveResults(filename = '/tmp/quota-diagnostic-results.json') {
    fs.writeFileSync(
      filename,
      JSON.stringify(
        {
          timestamp: this.timestamp,
          results: this.results,
          summary: {
            total: this.results.length,
            working: this.results.filter((r) => r.status === 'WORKS').length,
            failed: this.results.filter((r) => r.status !== 'WORKS').length,
          },
        },
        null,
        2,
      ),
    );
    console.log(`\n✅ Results saved to: ${filename}\n`);
  }
}

async function main() {
  const diagnostic = new QuotaDiagnostic();
  const command = process.argv[2] || 'all';

  try {
    if (command === 'all') {
      for (const provider of Object.keys(PROVIDERS)) {
        const results = await diagnostic.testProvider(provider);
        diagnostic.displayResults(results);
      }
    } else {
      const results = await diagnostic.testProvider(command);
      diagnostic.displayResults(results);
    }

    diagnostic.saveResults();
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { QuotaDiagnostic };
