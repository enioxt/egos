import {
  App,
  Editor,
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TFile,
  addIcon,
  WorkspaceLeaf
} from 'obsidian';

import { EGOSLLMSettingTab } from './settings-ui';
import { EGOSLLMSettings, DEFAULT_SETTINGS } from './settings';
import { AlibabaProvider } from './llm-providers/alibaba';
import { ClaudeProvider } from './llm-providers/claude';
import { CodexProvider } from './llm-providers/codex';
import { LLMProvider, ChatMessage } from './llm-providers/base';
import { ChatPanel, VIEW_TYPE_CHAT } from './ui/chat-panel';

export default class EGOSLLMPlugin extends Plugin {
  settings: EGOSLLMSettings;
  providers: Map<string, LLMProvider> = new Map();
  chatPanel: ChatPanel | null = null;

  async onload() {
    await this.loadSettings();

    // Initialize providers
    this.initializeProviders();

    // Register custom icon
    addIcon('egos-llm', `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
      <path d="M2 17l10 5 10-5"/>
      <path d="M2 12l10 5 10-5"/>
    </svg>`);

    // Register chat view
    this.registerView(
      VIEW_TYPE_CHAT,
      (leaf) => {
        this.chatPanel = new ChatPanel(leaf, this);
        return this.chatPanel;
      }
    );

    // Add ribbon icon
    this.addRibbonIcon('egos-llm', 'EGOS LLM Chat', () => {
      this.activateChatView();
    });

    // Add command palette commands
    this.addCommand({
      id: 'open-egos-llm-chat',
      name: 'Open LLM Chat',
      callback: () => {
        this.activateChatView();
      }
    });

    this.addCommand({
      id: 'ask-alibaba',
      name: 'Ask Alibaba (Qwen)',
      callback: () => {
        this.quickAsk('alibaba');
      }
    });

    this.addCommand({
      id: 'ask-claude',
      name: 'Ask Claude',
      callback: () => {
        this.quickAsk('claude');
      }
    });

    this.addCommand({
      id: 'ask-codex',
      name: 'Ask Codex',
      callback: () => {
        this.quickAsk('codex');
      }
    });

    this.addCommand({
      id: 'summarize-note',
      name: 'Summarize Current Note',
      editorCallback: (editor: Editor, view: MarkdownView) => {
        this.summarizeNote(editor, view);
      }
    });

    this.addCommand({
      id: 'generate-tags',
      name: 'Generate Tags for Note',
      editorCallback: (editor: Editor, view: MarkdownView) => {
        this.generateTags(editor, view);
      }
    });

    this.addCommand({
      id: 'login-codex',
      name: 'Login to Codex (Browser)',
      callback: () => {
        this.loginCodex();
      }
    });

    // Add settings tab
    this.addSettingTab(new EGOSLLMSettingTab(this.app, this));

    console.log('EGOS LLM Connector loaded');
  }

  onunload() {
    console.log('EGOS LLM Connector unloaded');
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
    this.initializeProviders();
  }

  initializeProviders() {
    this.providers.clear();

    if (this.settings.alibabaEnabled && this.settings.alibabaApiKey) {
      this.providers.set('alibaba', new AlibabaProvider(this.settings));
    }

    if (this.settings.claudeEnabled && this.settings.claudeApiKey) {
      this.providers.set('claude', new ClaudeProvider(this.settings));
    }

    if (this.settings.codexEnabled) {
      this.providers.set('codex', new CodexProvider(this.settings));
    }
  }

  async activateChatView() {
    const { workspace } = this.app;

    let leaf: WorkspaceLeaf | null = null;
    const leaves = workspace.getLeavesOfType(VIEW_TYPE_CHAT);

    if (leaves.length > 0) {
      leaf = leaves[0];
    } else {
      leaf = workspace.getRightLeaf(false);
      if (leaf) {
        await leaf.setViewState({ type: VIEW_TYPE_CHAT, active: true });
      }
    }

    if (leaf) {
      workspace.revealLeaf(leaf);
    }
  }

  async quickAsk(providerName: string) {
    const provider = this.providers.get(providerName);
    if (!provider) {
      new Notice(`${providerName} not configured. Check settings.`);
      return;
    }

    new QuickAskModal(this.app, provider, providerName).open();
  }

  async summarizeNote(editor: Editor, view: MarkdownView) {
    const content = editor.getValue();
    const provider = this.getDefaultProvider();
    
    if (!provider) {
      new Notice('No LLM provider configured');
      return;
    }

    new Notice('Summarizing...');
    
    try {
      const messages: ChatMessage[] = [
        { role: 'system', content: 'Summarize the following note concisely:' },
        { role: 'user', content }
      ];
      
      const response = await provider.chat(messages);
      
      // Insert summary at top of note
      editor.setCursor({ line: 0, ch: 0 });
      editor.replaceSelection(`> **Summary:** ${response}\n\n`);
      
      new Notice('Summary added!');
    } catch (error) {
      new Notice(`Error: ${error.message}`);
    }
  }

  async generateTags(editor: Editor, view: MarkdownView) {
    const content = editor.getValue();
    const provider = this.getDefaultProvider();
    
    if (!provider) {
      new Notice('No LLM provider configured');
      return;
    }

    new Notice('Generating tags...');
    
    try {
      const messages: ChatMessage[] = [
        { role: 'system', content: 'Generate 3-5 relevant tags for this note. Return only the tags separated by commas, no explanation.' },
        { role: 'user', content: content.substring(0, 2000) }
      ];
      
      const response = await provider.chat(messages);
      const tags = response.split(',').map((t: string) => t.trim()).filter((t: string) => t);
      
      // Add tags to frontmatter or bottom
      const tagString = tags.map((t: string) => `#${t.replace(/\s+/g, '-')}`).join(' ');
      editor.replaceSelection(`\n\n---\nTags: ${tagString}`);
      
      new Notice(`Tags: ${tags.join(', ')}`);
    } catch (error) {
      new Notice(`Error: ${error.message}`);
    }
  }

  async loginCodex() {
    const codexProvider = this.providers.get('codex') as CodexProvider;
    if (!codexProvider) {
      new Notice('Codex not enabled in settings');
      return;
    }
    
    await codexProvider.authenticate();
  }

  getDefaultProvider(): LLMProvider | undefined {
    if (this.settings.defaultProvider && this.providers.has(this.settings.defaultProvider)) {
      return this.providers.get(this.settings.defaultProvider);
    }
    return this.providers.values().next().value;
  }

  getProvider(name: string): LLMProvider | undefined {
    return this.providers.get(name);
  }
}

class QuickAskModal extends Modal {
  provider: LLMProvider;
  providerName: string;

  constructor(app: App, provider: LLMProvider, providerName: string) {
    super(app);
    this.provider = provider;
    this.providerName = providerName;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.createEl('h2', { text: `Ask ${this.providerName}` });

    const input = contentEl.createEl('textarea', {
      attr: { placeholder: 'Enter your question...', rows: 4 }
    });
    input.style.width = '100%';

    const button = contentEl.createEl('button', { text: 'Send' });
    button.style.marginTop = '10px';

    const responseDiv = contentEl.createEl('div');
    responseDiv.style.marginTop = '20px';
    responseDiv.style.whiteSpace = 'pre-wrap';

    button.addEventListener('click', async () => {
      const question = input.value;
      if (!question) return;

      button.disabled = true;
      button.textContent = 'Thinking...';

      try {
        const messages: ChatMessage[] = [
          { role: 'user', content: question }
        ];
        const response = await this.provider.chat(messages);
        responseDiv.textContent = response;
      } catch (error) {
        responseDiv.textContent = `Error: ${error.message}`;
      } finally {
        button.disabled = false;
        button.textContent = 'Send';
      }
    });

    contentEl.createEl('button', { text: 'Close' }).addEventListener('click', () => {
      this.close();
    });
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}
