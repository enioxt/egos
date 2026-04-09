#!/usr/bin/env bun
/**
 * Security Audit Script — EGOS
 * Scans dependencies for known vulnerabilities and security issues
 *
 * Usage: bun scripts/security-audit.ts [--fix] [--json]
 */

import { readFileSync, existsSync } from "fs";
import { join } from "path";

interface Vulnerability {
  package: string;
  currentVersion: string;
  cve: string;
  severity: "critical" | "high" | "moderate" | "low";
  fixVersion: string;
  description: string;
}

// Known vulnerabilities database
const KNOWN_VULNERABILITIES: Vulnerability[] = [
  {
    package: "axios",
    currentVersion: "<1.16.0",
    cve: "CVE-2024-39353",
    severity: "high",
    fixVersion: "1.16.0+",
    description: "XSS vulnerability in axios before 1.16.0",
  },
  {
    package: "axios",
    currentVersion: "<1.6.0",
    cve: "CVE-2023-45857",
    severity: "high",
    fixVersion: "1.6.0+",
    description: "CSRF vulnerability in axios before 1.6.0",
  },
  {
    package: "cross-spawn",
    currentVersion: "<7.0.6",
    cve: "CVE-2024-21538",
    severity: "high",
    fixVersion: "7.0.6+",
    description: "Prototype pollution in cross-spawn before 7.0.6",
  },
  {
    package: "ajv",
    currentVersion: "<8.17.1",
    cve: "CVE-2020-15366",
    severity: "moderate",
    fixVersion: "8.17.1+",
    description: "Prototype pollution in ajv before 8.17.1",
  },
  {
    package: "semver",
    currentVersion: "<7.5.2",
    cve: "CVE-2022-25883",
    severity: "moderate",
    fixVersion: "7.5.2+",
    description: "ReDoS in semver before 7.5.2",
  },
  {
    package: "ws",
    currentVersion: "<8.17.1",
    cve: "CVE-2024-37890",
    severity: "moderate",
    fixVersion: "8.17.1+",
    description: "DoS vulnerability in ws before 8.17.1",
  },
];

function parseLockfile(): Map<string, string> {
  const lockPath = join(process.cwd(), "bun.lock");
  if (!existsSync(lockPath)) {
    console.error("❌ bun.lock not found");
    process.exit(1);
  }

  const content = readFileSync(lockPath, "utf-8");
  const packages = new Map<string, string>();

  // Parse bun.lock format: "package@version": ["package@version", ...]
  const regex = /"([^"]+)@([^"]+)"\s*:\s*\["[^"]+@([^"]+)"/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const [, name, , version] = match;
    if (!packages.has(name) || isNewer(version, packages.get(name)!)) {
      packages.set(name, version);
    }
  }

  return packages;
}

function isNewer(v1: string, v2: string): boolean {
  const parse = (v: string) => v.split(".").map((n) => parseInt(n, 10));
  const p1 = parse(v1.replace(/[^0-9.]/g, ""));
  const p2 = parse(v2.replace(/[^0-9.]/g, ""));

  for (let i = 0; i < Math.max(p1.length, p2.length); i++) {
    const n1 = p1[i] || 0;
    const n2 = p2[i] || 0;
    if (n1 > n2) return true;
    if (n1 < n2) return false;
  }
  return false;
}

function versionInRange(version: string, range: string): boolean {
  const cleanVersion = version.replace(/[^0-9.]/g, "");
  const cleanRange = range.replace(/[^0-9.<>]/g, "");

  if (range.startsWith("<")) {
    const limit = cleanRange.replace(/</g, "");
    return !isNewer(cleanVersion, limit) && cleanVersion !== limit;
  }

  return false;
}

function audit(packages: Map<string, string>): Vulnerability[] {
  const found: Vulnerability[] = [];

  for (const vuln of KNOWN_VULNERABILITIES) {
    if (packages.has(vuln.package)) {
      const installedVersion = packages.get(vuln.package)!;
      if (versionInRange(installedVersion, vuln.currentVersion)) {
        found.push({ ...vuln, currentVersion: installedVersion });
      }
    }
  }

  return found.sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, moderate: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });
}

function formatSeverity(severity: string): string {
  const colors: Record<string, string> = {
    critical: "🔴",
    high: "🟠",
    moderate: "🟡",
    low: "🟢",
  };
  return `${colors[severity] || "⚪"} ${severity.toUpperCase()}`;
}

async function main() {
  const args = process.argv.slice(2);
  const jsonOutput = args.includes("--json");
  const fixMode = args.includes("--fix");

  if (!jsonOutput) {
    console.log("🔍 EGOS Security Audit\n");
  }

  const packages = parseLockfile();
  const vulnerabilities = audit(packages);

  if (jsonOutput) {
    console.log(JSON.stringify({ vulnerabilities, scanned: packages.size }, null, 2));
    process.exit(vulnerabilities.length > 0 ? 1 : 0);
  }

  console.log(`📦 Scanned ${packages.size} packages\n`);

  if (vulnerabilities.length === 0) {
    console.log("✅ No known vulnerabilities found!");
    process.exit(0);
  }

  const critical = vulnerabilities.filter((v) => v.severity === "critical").length;
  const high = vulnerabilities.filter((v) => v.severity === "high").length;
  const moderate = vulnerabilities.filter((v) => v.severity === "moderate").length;
  const low = vulnerabilities.filter((v) => v.severity === "low").length;

  console.log(`⚠️  Found ${vulnerabilities.length} vulnerabilities:`);
  console.log(`   🔴 Critical: ${critical}`);
  console.log(`   🟠 High: ${high}`);
  console.log(`   🟡 Moderate: ${moderate}`);
  console.log(`   🟢 Low: ${low}\n`);

  console.log("📋 Details:\n");
  for (const vuln of vulnerabilities) {
    console.log(`${formatSeverity(vuln.severity)} — ${vuln.package}@${vuln.currentVersion}`);
    console.log(`   CVE: ${vuln.cve}`);
    console.log(`   Fix: Update to ${vuln.fixVersion}`);
    console.log(`   ${vuln.description}\n`);
  }

  if (fixMode && vulnerabilities.length > 0) {
    console.log("🔧 Suggested fixes:");
    const uniquePackages = new Set(vulnerabilities.map((v) => v.package));
    for (const pkg of uniquePackages) {
      const latestVuln = vulnerabilities.find((v) => v.package === pkg);
      if (latestVuln) {
        console.log(`   bun update ${pkg}@${latestVuln.fixVersion.replace(/\+$/, "latest")}`);
      }
    }
  }

  console.log("\n📖 For more details, visit: https://github.com/enioxt/egos/security/dependabot");
  process.exit(1);
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});
