import { ItemView, WorkspaceLeaf, TFile, Notice } from 'obsidian';
import EGOSLLMPlugin from '../main';
import { ChatMessage } from '../llm-providers/base';

export const VIEW_TYPE_CHAT = 'egos-llm-chat';

export class ChatPanel extends ItemView {
  plugin: EGOSLLMPlugin;
  messages: ChatMessage[] = [];
  currentProvider: string = '';

  constructor(leaf: WorkspaceLeaf, plugin: EGOSLLMPlugin) {
    super(leaf);
    this.plugin = plugin;
    this.currentProvider = plugin.settings.defaultProvider;
  }

  getViewType(): string {
    return VIEW_TYPE_CHAT;
  }

  getDisplayText(): string {
    return 'EGOS LLM Chat';
  }

  getIcon(): string {
    return 'egos-llm';
  }

  async onOpen(): Promise<void> {
    this.containerEl.empty();
    this.render();
  }

  render(): void {
    const container = this.containerEl.createEl('div', { cls: 'egos-chat-container' });
    container.style.height = '100%';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';

    // Header
    const header = container.createEl('div', { cls: 'egos-chat-header' });
    header.style.padding = '10px';
    header.style.borderBottom = '1px solid var(--background-modifier-border)';
    header.style.display = 'flex';
    header.style.gap = '10px';
    header.style.alignItems = 'center';

    header.createEl('span', { text: 'Provider:' });
    
    const providerSelect = header.createEl('select');
    const providers = [
      { value: 'alibaba', label: 'Alibaba (Qwen)' },
      { value: 'claude', label: 'Claude' },
      { value: 'codex', label: 'Codex' },
    ];
    
    providers.forEach(p => {
      const option = providerSelect.createEl('option', { text: p.label, value: p.value });
      if (p.value === this.currentProvider) {
        option.selected = true;
      }
    });

    providerSelect.addEventListener('change', (e) => {
      this.currentProvider = (e.target as HTMLSelectElement).value;
    });

    // Clear chat button
    const clearBtn = header.createEl('button', { text: 'Clear' });
    clearBtn.style.marginLeft = 'auto';
    clearBtn.addEventListener('click', () => {
      this.messages = [];
      this.renderMessages();
    });

    // Messages area
    const messagesArea = container.createEl('div', { cls: 'egos-chat-messages' });
    messagesArea.style.flex = '1';
    messagesArea.style.overflow = 'auto';
    messagesArea.style.padding = '10px';
    this.messagesArea = messagesArea;

    // Input area
    const inputArea = container.createEl('div', { cls: 'egos-chat-input-area' });
    inputArea.style.padding = '10px';
    inputArea.style.borderTop = '1px solid var(--background-modifier-border)';
    inputArea.style.display = 'flex';
    inputArea.style.gap = '10px';

    const input = inputArea.createEl('textarea', {
      cls: 'egos-chat-input',
      attr: { placeholder: 'Type your message...', rows: '3' }
    });
    input.style.flex = '1';
    input.style.resize = 'none';

    const sendBtn = inputArea.createEl('button', { text: 'Send', cls: 'mod-cta' });
    sendBtn.addEventListener('click', () => this.sendMessage(input));

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.sendMessage(input);
      }
    });

    // Add context button
    const contextBtn = inputArea.createEl('button', { text: 'Add Note' });
    contextBtn.addEventListener('click', () => this.addCurrentNoteContext(input));

    this.renderMessages();
  }

  private messagesArea: HTMLElement;

  renderMessages(): void {
    this.messagesArea.empty();
    
    this.messages.forEach(msg => {
      const msgEl = this.messagesArea.createEl('div', { 
        cls: `egos-chat-message egos-chat-message-${msg.role}` 
      });
      msgEl.style.marginBottom = '10px';
      msgEl.style.padding = '8px 12px';
      msgEl.style.borderRadius = '8px';
      msgEl.style.maxWidth = '85%';
      
      if (msg.role === 'user') {
        msgEl.style.backgroundColor = 'var(--interactive-accent)';
        msgEl.style.color = 'var(--text-on-accent)';
        msgEl.style.marginLeft = 'auto';
      } else {
        msgEl.style.backgroundColor = 'var(--background-secondary)';
      }

      // Handle markdown-like formatting
      const content = msgEl.createEl('div');
      content.innerHTML = this.formatMessage(msg.content);
    });

    // Scroll to bottom
    this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
  }

  formatMessage(content: string): string {
    // Basic markdown formatting
    return content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  async sendMessage(input: HTMLTextAreaElement): Promise<void> {
    const content = input.value.trim();
    if (!content) return;

    const provider = this.plugin.getProvider(this.currentProvider);
    if (!provider) {
      new Notice(`${this.currentProvider} not configured. Check settings.`);
      return;
    }

    // Add user message
    this.messages.push({ role: 'user', content });
    input.value = '';
    this.renderMessages();

    // Show typing indicator
    const typingEl = this.messagesArea.createEl('div', { 
      text: 'Thinking...',
      cls: 'egos-chat-typing' 
    });
    typingEl.style.fontStyle = 'italic';
    typingEl.style.color = 'var(--text-muted)';
    this.messagesArea.scrollTop = this.messagesArea.scrollHeight;

    try {
      const response = await provider.chat(this.messages);
      
      // Remove typing indicator
      typingEl.remove();
      
      // Add assistant message
      this.messages.push({ role: 'assistant', content: response });
      this.renderMessages();
    } catch (error) {
      typingEl.remove();
      new Notice(`Error: ${error.message}`);
      
      // Add error message
      this.messages.push({ 
        role: 'assistant', 
        content: `Error: ${error.message}` 
      });
      this.renderMessages();
    }
  }

  async addCurrentNoteContext(input: HTMLTextAreaElement): Promise<void> {
    const activeFile = this.plugin.app.workspace.getActiveFile();
    if (!activeFile) {
      new Notice('No active note');
      return;
    }

    try {
      const content = await this.plugin.app.vault.read(activeFile);
      const context = `\n\n[Context from "${activeFile.name}"]:\n${content.substring(0, 2000)}${content.length > 2000 ? '...' : ''}`;
      
      input.value += context;
      new Notice(`Added context from ${activeFile.name}`);
    } catch (error) {
      new Notice(`Error reading file: ${error.message}`);
    }
  }

  async onClose(): Promise<void> {
    // Cleanup if needed
  }
}
