import { App, PluginSettingTab, Setting } from 'obsidian';
import EGOSLLMPlugin from './main';

export class EGOSLLMSettingTab extends PluginSettingTab {
  plugin: EGOSLLMPlugin;

  constructor(app: App, plugin: EGOSLLMPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    containerEl.createEl('h2', { text: 'EGOS LLM Connector Settings' });

    // Default Provider
    new Setting(containerEl)
      .setName('Default Provider')
      .setDesc('Select the default LLM provider for commands')
      .addDropdown(dropdown => {
        dropdown
          .addOption('alibaba', 'Alibaba DashScope (Qwen)')
          .addOption('claude', 'Claude (Anthropic)')
          .addOption('codex', 'Codex (OpenAI)')
          .setValue(this.plugin.settings.defaultProvider)
          .onChange(async (value) => {
            this.plugin.settings.defaultProvider = value;
            await this.plugin.saveSettings();
          });
      });

    // Alibaba Section
    containerEl.createEl('h3', { text: 'Alibaba DashScope (Qwen)' });

    new Setting(containerEl)
      .setName('Enable Alibaba')
      .setDesc('Enable Alibaba DashScope API')
      .addToggle(toggle => {
        toggle
          .setValue(this.plugin.settings.alibabaEnabled)
          .onChange(async (value) => {
            this.plugin.settings.alibabaEnabled = value;
            await this.plugin.saveSettings();
          });
      });

    new Setting(containerEl)
      .setName('API Key')
      .setDesc('Your Alibaba DashScope API Key (starts with sk-)')
      .addText(text => {
        text
          .setPlaceholder('sk-xxxxx')
          .setValue(this.plugin.settings.alibabaApiKey)
          .onChange(async (value) => {
            this.plugin.settings.alibabaApiKey = value;
            await this.plugin.saveSettings();
          });
        text.inputEl.type = 'password';
      });

    new Setting(containerEl)
      .setName('Model')
      .setDesc('Select Qwen model')
      .addDropdown(dropdown => {
        dropdown
          .addOption('qwen-plus', 'Qwen Plus (recommended)')
          .addOption('qwen-max', 'Qwen Max')
          .addOption('qwen-turbo', 'Qwen Turbo')
          .addOption('qwen-coder-plus', 'Qwen Coder Plus')
          .setValue(this.plugin.settings.alibabaModel)
          .onChange(async (value) => {
            this.plugin.settings.alibabaModel = value;
            await this.plugin.saveSettings();
          });
      });

    // Claude Section
    containerEl.createEl('h3', { text: 'Claude (Anthropic)' });

    new Setting(containerEl)
      .setName('Enable Claude')
      .setDesc('Enable Claude API')
      .addToggle(toggle => {
        toggle
          .setValue(this.plugin.settings.claudeEnabled)
          .onChange(async (value) => {
            this.plugin.settings.claudeEnabled = value;
            await this.plugin.saveSettings();
          });
      });

    new Setting(containerEl)
      .setName('API Key')
      .setDesc('Your Anthropic API Key')
      .addText(text => {
        text
          .setPlaceholder('sk-ant-xxxxx')
          .setValue(this.plugin.settings.claudeApiKey)
          .onChange(async (value) => {
            this.plugin.settings.claudeApiKey = value;
            await this.plugin.saveSettings();
          });
        text.inputEl.type = 'password';
      });

    new Setting(containerEl)
      .setName('Model')
      .setDesc('Select Claude model')
      .addDropdown(dropdown => {
        dropdown
          .addOption('claude-3-7-sonnet-20250219', 'Claude 3.7 Sonnet')
          .addOption('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet')
          .addOption('claude-3-opus-20240229', 'Claude 3 Opus')
          .addOption('claude-3-5-haiku-20241022', 'Claude 3.5 Haiku')
          .setValue(this.plugin.settings.claudeModel)
          .onChange(async (value) => {
            this.plugin.settings.claudeModel = value;
            await this.plugin.saveSettings();
          });
      });

    // Codex Section
    containerEl.createEl('h3', { text: 'Codex (OpenAI)' });

    new Setting(containerEl)
      .setName('Enable Codex')
      .setDesc('Enable Codex CLI integration (opens browser for auth)')
      .addToggle(toggle => {
        toggle
          .setValue(this.plugin.settings.codexEnabled)
          .onChange(async (value) => {
            this.plugin.settings.codexEnabled = value;
            await this.plugin.saveSettings();
          });
      });

    new Setting(containerEl)
      .setName('Session Token')
      .setDesc('Codex session token (auto-populated after browser login)')
      .addText(text => {
        text
          .setPlaceholder('auto-generated')
          .setValue(this.plugin.settings.codexSessionToken)
          .onChange(async (value) => {
            this.plugin.settings.codexSessionToken = value;
            await this.plugin.saveSettings();
          });
        text.inputEl.type = 'password';
        text.setDisabled(true);
      });

    const codexNote = containerEl.createEl('div');
    codexNote.createEl('p', { 
      text: 'To authenticate Codex: Open command palette → "EGOS LLM Connector: Login to Codex (Browser)"',
      cls: 'setting-item-description'
    });
    codexNote.style.marginTop = '10px';
    codexNote.style.color = 'var(--text-muted)';

    // Help section
    containerEl.createEl('hr');
    containerEl.createEl('h3', { text: 'Help & Links' });

    const helpDiv = containerEl.createEl('div');
    helpDiv.style.marginTop = '10px';
    
    helpDiv.createEl('a', {
      text: 'Get Alibaba API Key →',
      href: 'https://dashscope.console.aliyun.com/apiKey'
    });
    helpDiv.createEl('br');
    
    helpDiv.createEl('a', {
      text: 'Get Claude API Key →',
      href: 'https://console.anthropic.com/settings/keys'
    });
    helpDiv.createEl('br');
    
    helpDiv.createEl('a', {
      text: 'Codex Documentation →',
      href: 'https://github.com/openai/codex'
    });
  }
}
