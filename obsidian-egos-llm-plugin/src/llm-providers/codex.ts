import { LLMProvider, ChatMessage, ChatOptions } from './base';
import { EGOSLLMSettings } from '../settings';
import { requestUrl, Notice } from 'obsidian';

interface CodexAuthSession {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export class CodexProvider implements LLMProvider {
  name = 'Codex';
  settings: EGOSLLMSettings;
  private authServer: string = 'https://auth.openai.com';
  private apiServer: string = 'https://api.openai.com';
  private clientId: string = 'codex-cli';
  private redirectUri: string = 'http://localhost:8080/callback';

  constructor(settings: EGOSLLMSettings) {
    this.settings = settings;
  }

  isAvailable(): boolean {
    return this.settings.codexEnabled && !!this.settings.codexSessionToken;
  }

  async authenticate(): Promise<void> {
    // Generate PKCE code verifier and challenge
    const codeVerifier = this.generateCodeVerifier();
    const codeChallenge = await this.generateCodeChallenge(codeVerifier);
    const state = this.generateState();

    // Build authorization URL
    const authUrl = new URL(`${this.authServer}/authorize`);
    authUrl.searchParams.set('client_id', this.clientId);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('redirect_uri', this.redirectUri);
    authUrl.searchParams.set('code_challenge', codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');
    authUrl.searchParams.set('state', state);
    authUrl.searchParams.set('scope', 'openid profile email api.read api.write');

    // Open browser for authentication
    window.open(authUrl.toString(), '_blank');
    
    new Notice('Browser opened for Codex authentication. Complete login and paste the code here.');

    // Show modal to enter authorization code
    const code = await this.promptForAuthCode();
    
    if (!code) {
      throw new Error('Authentication cancelled');
    }

    // Exchange code for tokens
    await this.exchangeCodeForTokens(code, codeVerifier);
  }

  private generateCodeVerifier(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  private async generateCodeChallenge(verifier: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(verifier);
    const digest = await crypto.subtle.digest('SHA-256', data);
    return btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  private generateState(): string {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array));
  }

  private async promptForAuthCode(): Promise<string | null> {
    return new Promise((resolve) => {
      const modal = document.createElement('div');
      modal.className = 'modal-container';
      modal.innerHTML = `
        <div class="modal">
          <div class="modal-content">
            <h3>Codex Authentication</h3>
            <p>After logging in the browser, paste the authorization code here:</p>
            <input type="text" id="auth-code" placeholder="Enter code..." style="width: 100%; margin: 10px 0;">
            <div class="modal-button-container">
              <button id="confirm-btn">Confirm</button>
              <button id="cancel-btn">Cancel</button>
            </div>
          </div>
        </div>
      `;
      
      document.body.appendChild(modal);
      
      const input = modal.querySelector('#auth-code') as HTMLInputElement;
      const confirmBtn = modal.querySelector('#confirm-btn') as HTMLButtonElement;
      const cancelBtn = modal.querySelector('#cancel-btn') as HTMLButtonElement;
      
      confirmBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
        resolve(input.value);
      });
      
      cancelBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
        resolve(null);
      });
      
      input.focus();
    });
  }

  private async exchangeCodeForTokens(code: string, codeVerifier: string): Promise<void> {
    const response = await requestUrl({
      url: `${this.authServer}/token`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.clientId,
        code: code,
        code_verifier: codeVerifier,
        redirect_uri: this.redirectUri,
      }).toString(),
    });

    if (response.status !== 200) {
      throw new Error(`Token exchange failed: ${response.text}`);
    }

    const data = JSON.parse(response.text);
    
    // Save tokens to settings
    this.settings.codexSessionToken = data.access_token;
    this.settings.codexRefreshToken = data.refresh_token;
    
    // Note: In a real implementation, you'd save these via the plugin's saveSettings()
    new Notice('Codex authentication successful!');
  }

  async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
    // Codex uses OpenAI's API format
    const response = await requestUrl({
      url: `${this.apiServer}/v1/chat/completions`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.settings.codexSessionToken}`,
      },
      body: JSON.stringify({
        model: 'o3-mini', // Codex default model
        messages: messages,
        temperature: options?.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? 4096,
      }),
    });

    if (response.status !== 200) {
      throw new Error(`Codex API error: ${response.status} - ${response.text}`);
    }

    const data = JSON.parse(response.text);
    return data.choices[0]?.message?.content || '';
  }

  async refreshToken(): Promise<void> {
    if (!this.settings.codexRefreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await requestUrl({
      url: `${this.authServer}/token`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: this.clientId,
        refresh_token: this.settings.codexRefreshToken,
      }).toString(),
    });

    if (response.status !== 200) {
      throw new Error(`Token refresh failed: ${response.text}`);
    }

    const data = JSON.parse(response.text);
    this.settings.codexSessionToken = data.access_token;
    
    if (data.refresh_token) {
      this.settings.codexRefreshToken = data.refresh_token;
    }
  }
}
