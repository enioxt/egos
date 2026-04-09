#!/usr/bin/env bun
/**
 * X-COM-010: Thread Composer Web Interface
 * Componente para criação de threads X.com via interface web
 * 
 * @task X-COM-010
 * @priority P1
 */

import { serve } from "bun";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const PORT = process.env.THREAD_COMPOSER_PORT || "3099";
const HQ_API = process.env.HQ_API_URL || "http://localhost:3002";

interface ThreadPost {
  id: string;
  content: string;
  media?: string[];
  scheduleAt?: string;
}

interface Thread {
  id: string;
  title: string;
  posts: ThreadPost[];
  status: "draft" | "scheduled" | "published";
  createdAt: string;
  updatedAt: string;
}

// HTML template for thread composer
const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>X Thread Composer — EGOS</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
      color: #e0e0e0;
      min-height: 100vh;
      padding: 2rem;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    h1 {
      font-size: 1.75rem;
      margin-bottom: 0.5rem;
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .subtitle {
      color: #888;
      margin-bottom: 2rem;
    }
    .thread-editor {
      background: rgba(255,255,255,0.05);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1rem;
    }
    .post-card {
      background: rgba(0,0,0,0.3);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
      position: relative;
    }
    .post-number {
      position: absolute;
      top: -10px;
      left: 10px;
      background: #7b2cbf;
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.75rem;
      font-weight: bold;
    }
    textarea {
      width: 100%;
      background: transparent;
      border: none;
      color: #e0e0e0;
      font-size: 1rem;
      resize: vertical;
      min-height: 80px;
      font-family: inherit;
    }
    textarea:focus {
      outline: none;
    }
    .char-count {
      text-align: right;
      font-size: 0.75rem;
      color: #666;
      margin-top: 0.5rem;
    }
    .char-count.warning { color: #ff9500; }
    .char-count.danger { color: #ff3b30; }
    .actions {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
    }
    button {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
    }
    .btn-primary {
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      color: white;
    }
    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(0,212,255,0.3);
    }
    .btn-secondary {
      background: rgba(255,255,255,0.1);
      color: #e0e0e0;
    }
    .btn-secondary:hover {
      background: rgba(255,255,255,0.15);
    }
    .btn-danger {
      background: rgba(255,59,48,0.2);
      color: #ff3b30;
    }
    .metadata {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }
    .metadata input {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 6px;
      padding: 0.5rem 1rem;
      color: #e0e0e0;
      font-size: 0.9rem;
    }
    .metadata input:focus {
      outline: none;
      border-color: #7b2cbf;
    }
    .total-stats {
      background: rgba(0,212,255,0.1);
      border-left: 3px solid #00d4ff;
      padding: 1rem;
      border-radius: 0 8px 8px 0;
      margin-bottom: 1rem;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 1rem;
    }
    .stat-item {
      text-align: center;
    }
    .stat-value {
      font-size: 1.5rem;
      font-weight: bold;
      color: #00d4ff;
    }
    .stat-label {
      font-size: 0.75rem;
      color: #888;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🧵 X Thread Composer</h1>
    <p class="subtitle">Crie threads otimizadas para engajamento</p>
    
    <div class="total-stats">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value" id="total-posts">1</div>
          <div class="stat-label">Posts</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="total-chars">0</div>
          <div class="stat-label">Caracteres</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="est-engagement">—</div>
          <div class="stat-label">Eng. Est.</div>
        </div>
      </div>
    </div>
    
    <div class="thread-editor">
      <div class="metadata">
        <input type="text" id="thread-title" placeholder="Título da thread (interno)" />
        <input type="datetime-local" id="schedule-time" />
      </div>
      
      <div id="posts-container">
        <div class="post-card" data-post-id="1">
          <span class="post-number">1</span>
          <textarea placeholder="Primeiro post da thread... (hook forte)" maxlength="280"></textarea>
          <div class="char-count">0/280</div>
        </div>
      </div>
      
      <div class="actions">
        <button class="btn-secondary" onclick="addPost()">+ Adicionar Post</button>
        <button class="btn-primary" onclick="saveThread()">💾 Salvar Rascunho</button>
        <button class="btn-primary" onclick="scheduleThread()">📅 Agendar</button>
        <button class="btn-danger" onclick="clearAll()">🗑️ Limpar</button>
      </div>
    </div>
  </div>
  
  <script>
    let postCount = 1;
    
    function updateCharCount(textarea) {
      const count = textarea.value.length;
      const counter = textarea.parentElement.querySelector('.char-count');
      counter.textContent = count + '/280';
      counter.className = 'char-count';
      if (count > 250) counter.className = 'char-count warning';
      if (count > 280) counter.className = 'char-count danger';
      updateTotalStats();
    }
    
    function updateTotalStats() {
      const textareas = document.querySelectorAll('textarea');
      let total = 0;
      textareas.forEach(t => total += t.value.length);
      document.getElementById('total-posts').textContent = postCount;
      document.getElementById('total-chars').textContent = total;
      
      // Simple engagement estimation based on content quality signals
      const firstPost = textareas[0]?.value || '';
      let score = 50;
      if (firstPost.includes('?')) score += 10;
      if (firstPost.includes('🔥') || firstPost.includes('💡')) score += 5;
      if (total > 500) score += 10;
      if (postCount >= 3 && postCount <= 7) score += 15;
      document.getElementById('est-engagement').textContent = score + '%';
    }
    
    function addPost() {
      postCount++;
      const container = document.getElementById('posts-container');
      const card = document.createElement('div');
      card.className = 'post-card';
      card.innerHTML = \`
        <span class="post-number">\${postCount}</span>
        <textarea placeholder="Continuação da thread..." maxlength="280"></textarea>
        <div class="char-count">0/280</div>
      \`;
      container.appendChild(card);
      card.querySelector('textarea').addEventListener('input', function() {
        updateCharCount(this);
      });
    }
    
    function saveThread() {
      const posts = [];
      document.querySelectorAll('.post-card').forEach((card, i) => {
        posts.push({
          id: i + 1,
          content: card.querySelector('textarea').value,
          media: []
        });
      });
      
      const thread = {
        id: 'thread_' + Date.now(),
        title: document.getElementById('thread-title').value || 'Sem título',
        posts,
        status: 'draft',
        createdAt: new Date().toISOString()
      };
      
      // Save to localStorage
      const threads = JSON.parse(localStorage.getItem('x_threads') || '[]');
      threads.push(thread);
      localStorage.setItem('x_threads', JSON.stringify(threads));
      
      alert('Thread salva! ID: ' + thread.id);
    }
    
    function scheduleThread() {
      const scheduleTime = document.getElementById('schedule-time').value;
      if (!scheduleTime) {
        alert('Selecione um horário para agendamento');
        return;
      }
      alert('Thread agendada para: ' + scheduleTime);
    }
    
    function clearAll() {
      if (confirm('Limpar todos os posts?')) {
        document.getElementById('posts-container').innerHTML = \`
          <div class="post-card" data-post-id="1">
            <span class="post-number">1</span>
            <textarea placeholder="Primeiro post da thread... (hook forte)" maxlength="280"></textarea>
            <div class="char-count">0/280</div>
          </div>
        \`;
        postCount = 1;
        updateTotalStats();
        setupListeners();
      }
    }
    
    function setupListeners() {
      document.querySelectorAll('textarea').forEach(t => {
        t.addEventListener('input', function() {
          updateCharCount(this);
        });
      });
    }
    
    // Initialize
    setupListeners();
    updateTotalStats();
  </script>
</body>
</html>`;

// Store threads in memory (would be Supabase in production)
const threads: Thread[] = [];

const server = serve({
  port: parseInt(PORT),
  async fetch(req) {
    const url = new URL(req.url);
    
    // Serve HTML interface
    if (url.pathname === "/" || url.pathname === "/composer") {
      return new Response(HTML_TEMPLATE, {
        headers: { "Content-Type": "text/html" }
      });
    }
    
    // API: Save thread
    if (url.pathname === "/api/thread" && req.method === "POST") {
      const body = await req.json();
      const thread: Thread = {
        id: `thread_${Date.now()}`,
        title: body.title || "Sem título",
        posts: body.posts || [],
        status: body.status || "draft",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      threads.push(thread);
      
      return Response.json({ success: true, thread });
    }
    
    // API: List threads
    if (url.pathname === "/api/threads" && req.method === "GET") {
      return Response.json({ threads });
    }
    
    // API: Health check
    if (url.pathname === "/health") {
      return Response.json({ 
        status: "ok", 
        service: "x-thread-composer",
        version: "0.1.0",
        threadsCount: threads.length
      });
    }
    
    return new Response("Not Found", { status: 404 });
  }
});

console.log(`🧵 X Thread Composer rodando em http://localhost:${PORT}`);
console.log(`📚 Endpoints:`);
console.log(`   GET  /          - Interface web`);
console.log(`   GET  /health    - Health check`);
console.log(`   POST /api/thread - Criar thread`);
console.log(`   GET  /api/threads - Listar threads`);
