#!/usr/bin/env bun
/**
 * OSINT-007: DM Templates para Delegacias
 * Templates específicos para PCMG, PMMG, PF
 * 
 * @task OSINT-007
 * @priority P1
 */

interface DMTemplate {
  id: string;
  orgao: "PCMG" | "PMMG" | "PF" | "PCPE" | "PCSP" | "PCGO" | "general";
  context: "cold_outreach" | "follow_up" | "case_collaboration" | "training" | "partnership";
  tone: "formal" | "consultative" | "technical";
  subject?: string;
  body: string;
  cta: string;
  variables: string[];
  followUpSequence?: number[]; // dias para follow-up
}

const DM_TEMPLATES: DMTemplate[] = [
  // PCMG Templates
  {
    id: "pcmg-cold-001",
    orgao: "PCMG",
    context: "cold_outreach",
    tone: "consultative",
    body: `Prezado(a) {{cargo}} {{nome}},

Sou Enio Rocha, fundador da EGOS Inteligência. Acompanho o trabalho da PCMG em {{area_atuacao}} e identifiquei uma oportunidade de colaboração.

Desenvolvemos uma plataforma de **cruzamento de dados públicos** que já ajudou órgãos similares a:
- Reduzir 40% do tempo em análise de vínculos empresariais
- Identificar padrões de movimentação financeira em casos de lavagem
- Automatizar consultas a dados públicos (CNPJ, sócios, endereços)

**Tudo em conformidade com LGPD** — pseudonimização de dados sensíveis e auditoria completa.

Gostaria de apresentar um case similar ao que a {{unidade}} investiga atualmente?`,
    cta: "Posso enviar um brief técnico de 5 min de leitura?",
    variables: ["cargo", "nome", "area_atuacao", "unidade"],
    followUpSequence: [3, 7, 14]
  },
  {
    id: "pcmg-case-001",
    orgao: "PCMG",
    context: "case_collaboration",
    tone: "technical",
    body: `{{cargo}} {{nome}},

Em apoio à investigação {{numero_caso}}, nossa equipe realizou uma análise preliminar usando dados públicos:

🔍 **Cruzamentos identificados:**
{{resultados_analise}}

📊 **Base de dados consultada:**
- 77M+ CNPJs
- 25M+ vínculos societários  
- Dados cartorários ({{uf}})
- Histórico de endereços

Estes achados podem ser **reproduzidos e auditados**. Posso disponibilizar a query Cypher utilizada?

{{nota_lgpd}}`,
    cta: "Quer agendar uma call técnica para discutir estes resultados?",
    variables: ["cargo", "nome", "numero_caso", "resultados_analise", "uf", "nota_lgpd"]
  },

  // PMMG Templates
  {
    id: "pmmg-training-001",
    orgao: "PMMG",
    context: "training",
    tone: "consultative",
    body: `Prezado Comandante {{nome}},

A PMMG tem sido referência em modernização policial no Brasil. Gostaria de propor uma **capacitação gratuita** para a equipe de inteligência da {{batalhao}}.

**Workshop: "OSINT para Polícia Militar"**
- Duração: 4h
- Formato: presencial ou remoto
- Conteúdo:
  • Consulta a dados públicos (CNPJ, veículos, propriedades)
  • Análise de redes sociais em investigações
  • LGPD na prática policial
  • Ferramentas open-source de inteligência

Sem compromisso comercial — nosso objetivo é fortalecer a rede de inteligência policial em MG.`,
    cta: "Posso enviar o programa completo do workshop?",
    variables: ["nome", "batalhao"]
  },
  {
    id: "pmmg-partnership-001",
    orgao: "PMMG",
    context: "partnership",
    tone: "formal",
    body: `Ilmo. Sr. Comandante {{nome}},

A EGOS Inteligência vem por meio desta manifestar interesse em estabelecer **convênio de cooperação técnica** com a {{batalhao}}/PMMG.

**Proposta de parceria:**
1. Disponibilização de acesso à plataforma EGOS para fins de pesquisa
2. Suporte técnico especializado para casos prioritários
3. Relatórios trimestrais de análise de padrões criminais em {{regiao}}
4. Capacitação contínua da equipe de inteligência

**Contrapartida:** Feedback técnico para melhoria da plataforma e autorização para uso de cases anonimizados em pesquisa acadêmica.

Esta parceria foi validada juridicamente e está em conformidade com a Lei 13.709/2018 (LGPD).`,
    cta: "Podemos agendar uma reunião formal para discutir termos?",
    variables: ["nome", "batalhao", "regiao"]
  },

  // PF Templates
  {
    id: "pf-osint-001",
    orgao: "PF",
    context: "cold_outreach",
    tone: "formal",
    body: `Senhor(a) Delegado(a) {{nome}},

Sou fundador da EGOS Inteligência, plataforma de análise de dados públicos brasileiros com foco em investigações complexas.

Identifiquei que a {{delegacia}} trabalha com {{tipo_investigacao}} — área onde nossa plataforma tem cases documentados:

**Exemplo de aplicação:**
- Análise de {{quantidade}} CNPJs em {{tempo}} de execução
- Identificação de {{percentual}}% de sócios em comum entre empresas-suspeitas
- Mapeamento de endereços fiscais vs. endereços reais
- Alertas de alterações cadastrais suspeitas

Operamos com **zero acesso a dados sigilosos** — apenas dados públicos e técnicas de cruzamento.

Posso enviar uma apresentação técnica para avaliação?`,
    cta: "Posso enviar apresentação técnica em PDF?",
    variables: ["nome", "delegacia", "tipo_investigacao", "quantidade", "tempo", "percentual"]
  },
  {
    id: "pf-coord-001",
    orgao: "PF",
    context: "partnership",
    tone: "formal",
    body: `Ilustríssimo(a) Delegado(a) {{nome}},

Em referência à operação {{nome_operacao}}, gostaria de oferecer **apoio técnico gratuito** da EGOS Inteligência.

**Recursos disponíveis:**
- Consulta massiva a CNPJs/sócios (batch de até 10k)
- Análise de grafos de relacionamento
- Detecção de padrões de evasão fiscal
- Cross-reference com dados de licitações (PNCP)

**LGPD Compliance:**
✓ Pseudonimização de dados pessoais
✓ Auditoria de todas as consultas
✓ Nenhum dado armazenado permanentemente
✓ Relatório de conformidade gerado automaticamente

Esta oferta é válida para apoio a investigações oficiais, sem fins lucrativos diretos.`,
    cta: "Posso enviar termo de confidencialidade e cooperação?",
    variables: ["nome", "nome_operacao"]
  },

  // Templates Genéricos
  {
    id: "general-followup-001",
    orgao: "general",
    context: "follow_up",
    tone: "consultative",
    body: `{{nome}},

Seguindo nossa conversa sobre {{topico_anterior}}, gostaria de compartilhar uma atualização:

{{atualizacao_relevante}}

Isso impacta diretamente o que discutimos sobre {{ponto_interesse}}.

Ainda faz sentido falarmos sobre {{proximo_passo}}?`,
    cta: "Posso ligar por 10 minutos esta semana?",
    variables: ["nome", "topico_anterior", "atualizacao_relevante", "ponto_interesse", "proximo_passo"]
  },
  {
    id: "general-value-001",
    orgao: "general",
    context: "cold_outreach",
    tone: "technical",
    body: `{{cargo}} {{nome}},

Trabalho com {{area_especialidade}} e notei que {{observacao_personalizada}}.

Recentemente ajudei {{case_similar}} a {{resultado_atingido}} usando {{tecnica_especifica}}.

Posso te mostrar como isso se aplicaria ao seu contexto?`,
    cta: "Topa uma conversa de 15 minutos?",
    variables: ["cargo", "nome", "area_especialidade", "observacao_personalizada", "case_similar", "resultado_atingido", "tecnica_especifica"]
  }
];

class DMTemplateManager {
  getByOrgao(orgao: DMTemplate["orgao"]): DMTemplate[] {
    return DM_TEMPLATES.filter(t => t.orgao === orgao || t.orgao === "general");
  }

  getByContext(context: DMTemplate["context"]): DMTemplate[] {
    return DM_TEMPLATES.filter(t => t.context === context);
  }

  getById(id: string): DMTemplate | undefined {
    return DM_TEMPLATES.find(t => t.id === id);
  }

  render(templateId: string, variables: Record<string, string>): { subject?: string; body: string; cta: string } {
    const template = this.getById(templateId);
    if (!template) {
      throw new Error(`Template ${templateId} não encontrado`);
    }

    let body = template.body;
    for (const [key, value] of Object.entries(variables)) {
      body = body.replace(new RegExp(`{{${key}}}`, "g"), value);
    }

    return {
      subject: template.subject,
      body,
      cta: template.cta
    };
  }

  suggestTemplate(orgao: DMTemplate["orgao"], context: DMTemplate["context"]): DMTemplate[] {
    return DM_TEMPLATES.filter(t => 
      (t.orgao === orgao || t.orgao === "general") && 
      t.context === context
    );
  }

  getFollowUpSequence(templateId: string): number[] {
    const template = this.getById(templateId);
    return template?.followUpSequence || [3, 7];
  }

  listAll(): { id: string; orgao: string; context: string; tone: string; preview: string }[] {
    return DM_TEMPLATES.map(t => ({
      id: t.id,
      orgao: t.orgao,
      context: t.context,
      tone: t.tone,
      preview: t.body.substring(0, 100) + "..."
    }));
  }

  stats(): { total: number; byOrgao: Record<string, number>; byContext: Record<string, number> } {
    const byOrgao: Record<string, number> = {};
    const byContext: Record<string, number> = {};

    for (const t of DM_TEMPLATES) {
      byOrgao[t.orgao] = (byOrgao[t.orgao] || 0) + 1;
      byContext[t.context] = (byContext[t.context] || 0) + 1;
    }

    return {
      total: DM_TEMPLATES.length,
      byOrgao,
      byContext
    };
  }
}

// CLI interface
async function main() {
  const manager = new DMTemplateManager();
  const command = process.argv[2];

  switch (command) {
    case "list": {
      const orgao = process.argv[3] as DMTemplate["orgao"];
      
      if (orgao) {
        const templates = manager.getByOrgao(orgao);
        console.log(`\n📋 Templates para ${orgao.toUpperCase()}:`);
        templates.forEach(t => {
          console.log(`\n${t.id} [${t.context}] — ${t.tone}`);
          console.log(`   ${t.body.substring(0, 80)}...`);
        });
      } else {
        console.log("\n📊 Stats de Templates:");
        console.log(manager.stats());
      }
      break;
    }

    case "render": {
      const templateId = process.argv[3];
      if (!templateId) {
        console.log("Uso: bun osint-dm-templates.ts render <template_id> key=value key2=value2");
        process.exit(1);
      }

      const vars: Record<string, string> = {};
      for (let i = 4; i < process.argv.length; i++) {
        const [key, value] = process.argv[i].split("=");
        if (key && value) vars[key] = value;
      }

      try {
        const rendered = manager.render(templateId, vars);
        console.log("\n📧 Template Renderizado:\n");
        console.log(rendered.body);
        console.log(`\n💬 CTA: ${rendered.cta}`);
      } catch (e) {
        console.error("❌ Erro:", e);
      }
      break;
    }

    case "suggest": {
      const orgao = (process.argv[3] || "general") as DMTemplate["orgao"];
      const context = (process.argv[4] || "cold_outreach") as DMTemplate["context"];

      const suggestions = manager.suggestTemplate(orgao, context);
      console.log(`\n💡 Sugestões para ${orgao} + ${context}:`);
      suggestions.forEach(t => {
        console.log(`\n${t.id} (${t.tone})`);
        console.log(`   ${t.body.substring(0, 100)}...`);
      });
      break;
    }

    case "followup": {
      const templateId = process.argv[3];
      if (!templateId) {
        console.log("Uso: bun osint-dm-templates.ts followup <template_id>");
        process.exit(1);
      }

      const sequence = manager.getFollowUpSequence(templateId);
      console.log(`\n📅 Sequência de follow-up para ${templateId}:`);
      console.log(`   Dias: ${sequence.join(", ")}`);
      break;
    }

    default:
      console.log(`
📨 OSINT DM Templates — OSINT-007

Comandos:
  list [orgao]              Listar templates (PCMG, PMMG, PF, general)
  render <id> k=v k2=v2     Renderizar template com variáveis
  suggest <orgao> <context>   Sugerir template para situação
  followup <id>             Ver sequência de follow-up

Exemplos:
  bun osint-dm-templates.ts list PCMG
  bun osint-dm-templates.ts render pcmg-cold-001 nome=Silva cargo=Delegado area_atuacao=Inteligencia unidade=DEIC

Contextos: cold_outreach, follow_up, case_collaboration, training, partnership
      `);
  }
}

if (import.meta.main) {
  main();
}

export { DMTemplateManager, DM_TEMPLATES, type DMTemplate };
