export type IntegrationChannel = 'slack' | 'discord' | 'telegram' | 'whatsapp' | 'webhook' | 'github' | 'custom';
export type IntegrationAuthType = 'oauth' | 'api-key' | 'bot-token' | 'custom';
export type IntegrationStatus = 'contract_only' | 'draft' | 'pilot' | 'validated' | 'deprecated';
export type IntegrationDistributionKind = 'npm' | 'docker' | 'docker-compose' | 'mcp' | 'api' | 'binary' | 'custom';
export type IntegrationProofKind = 'code' | 'log' | 'endpoint' | 'runbook' | 'manual';

export interface IntegrationDocumentationRefs {
  ssot: string;
  setup: string;
  runbook: string;
}

export interface IntegrationRuntimeProof {
  kind: IntegrationProofKind;
  ref: string;
  verifiedAt?: string;
  verifier?: string;
}

export interface IntegrationDistribution {
  kind: IntegrationDistributionKind;
  artifactRef: string;
  installCommand: string;
  envExampleRef?: string;
}

export interface IntegrationValidation {
  smokeCommand: string;
  evidenceRefs?: string[];
}

export interface IntegrationManifest {
  id: string;
  channel: IntegrationChannel;
  name: string;
  version: string;
  owner: string;
  status: IntegrationStatus;
  authType: IntegrationAuthType;
  events: string[];
  actions: string[];
  documentation: IntegrationDocumentationRefs;
  runtimeProof: IntegrationRuntimeProof[];
  distribution: IntegrationDistribution;
  validation: IntegrationValidation;
  configSchemaRef?: string;
}

export interface EgosIntegration {
  manifest: IntegrationManifest;
  connect(): Promise<void>;
  disconnect?(): Promise<void>;
}

export function validateIntegrationManifest(manifest: IntegrationManifest): string[] {
  const errors: string[] = [];
  const required = ['id', 'channel', 'name', 'version', 'owner', 'status', 'authType'] as const;

  for (const field of required) {
    if (!manifest[field]) errors.push(`missing ${field}`);
  }
  if (!/^\d+\.\d+\.\d+$/.test(manifest.version)) errors.push(`invalid semver: ${manifest.version}`);
  if (!manifest.documentation?.ssot || !manifest.documentation?.setup || !manifest.documentation?.runbook) {
    errors.push('documentation contract incomplete');
  }
  if (!manifest.validation?.smokeCommand) errors.push('missing validation.smokeCommand');
  if (!manifest.events?.length) errors.push('missing events');
  if (!manifest.actions?.length) errors.push('missing actions');
  if (manifest.status !== 'contract_only' && !manifest.runtimeProof?.length) errors.push('missing runtimeProof');
  if (manifest.status !== 'contract_only' && !manifest.distribution?.artifactRef) {
    errors.push('missing distribution artifactRef');
  }

  return errors;
}
