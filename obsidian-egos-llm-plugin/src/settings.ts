export interface EGOSLLMSettings {
  // General
  defaultProvider: string;

  // Alibaba DashScope
  alibabaEnabled: boolean;
  alibabaApiKey: string;
  alibabaModel: string;
  alibabaBaseUrl: string;

  // Claude
  claudeEnabled: boolean;
  claudeApiKey: string;
  claudeModel: string;
  claudeBaseUrl: string;

  // Codex
  codexEnabled: boolean;
  codexSessionToken: string;
  codexRefreshToken: string;
}

export const DEFAULT_SETTINGS: EGOSLLMSettings = {
  defaultProvider: 'alibaba',

  alibabaEnabled: true,
  alibabaApiKey: '',
  alibabaModel: 'qwen-plus',
  alibabaBaseUrl: 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1',

  claudeEnabled: false,
  claudeApiKey: '',
  claudeModel: 'claude-3-7-sonnet-20250219',
  claudeBaseUrl: 'https://api.anthropic.com/v1',

  codexEnabled: false,
  codexSessionToken: '',
  codexRefreshToken: '',
};
