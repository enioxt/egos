#!/usr/bin/env bun
/**
 * OSINT-006: Brasil.IO + Escavador + Jusbrasil Integration Wrapper
 * Unificação de APIs de dados públicos brasileiros
 * 
 * @task OSINT-006
 * @priority P1
 */

interface BrasilIOResult {
  cnpj?: string;
  razao_social?: string;
  nome_fantasia?: string;
  situacao?: string;
  data_abertura?: string;
  endereco?: {
    logradouro: string;
    numero: string;
    bairro: string;
    municipio: string;
    uf: string;
    cep: string;
  };
  atividade_principal?: { code: string; description: string };
  socios?: Array<{ nome: string; qualificacao: string }>;
}

interface EscavadorResult {
  pessoa?: {
    nome: string;
    cpf?: string;
    vinculos?: Array<{
      empresa: string;
      cargo: string;
      periodo: string;
    }>;
  };
  empresa?: {
    cnpj: string;
    nome: string;
    processos?: Array<{
      numero: string;
      tribunal: string;
      partes: string[];
    }>;
  };
}

interface JusbrasilResult {
  processo?: {
    numero: string;
    classe: string;
    assunto: string;
    foro: string;
    vara: string;
    partes: Array<{ nome: string; tipo: string }>;
    movimentacoes: Array<{ data: string; descricao: string }>;
  };
  diario?: {
    data: string;
    caderno: string;
    secao: string;
    conteudo: string;
  };
}

class OSINTBrasilWrapper {
  private brasilIOToken: string;
  private escavadorToken: string;
  private jusbrasilToken: string;

  constructor() {
    this.brasilIOToken = process.env.BRASIL_IO_TOKEN || "";
    this.escavadorToken = process.env.ESCAVADOR_TOKEN || "";
    this.jusbrasilToken = process.env.JUSBRASIL_TOKEN || "";
  }

  async queryBrasilIO(cnpj: string): Promise<BrasilIOResult | null> {
    if (!this.brasilIOToken) {
      console.warn("⚠️ BRASIL_IO_TOKEN não configurado");
      return this.mockBrasilIO(cnpj);
    }

    try {
      const response = await fetch(
        `https://api.brasil.io/v1/dataset/socios-brasil/data/${cnpj}/`,
        {
          headers: {
            "Authorization": `Token ${this.brasilIOToken}`,
            "User-Agent": "EGOS-OSINT/1.0"
          }
        }
      );

      if (!response.ok) return null;
      return await response.json();
    } catch {
      return this.mockBrasilIO(cnpj);
    }
  }

  async queryEscavador(nome: string, type: "pessoa" | "empresa" = "pessoa"): Promise<EscavadorResult | null> {
    if (!this.escavadorToken) {
      console.warn("⚠️ ESCAVADOR_TOKEN não configurado");
      return this.mockEscavador(nome);
    }

    try {
      const endpoint = type === "pessoa" 
        ? `/v2/pessoas?q=${encodeURIComponent(nome)}`
        : `/v2/empresas?q=${encodeURIComponent(nome)}`;
      
      const response = await fetch(`https://api.escavador.com${endpoint}`, {
        headers: {
          "Authorization": `Bearer ${this.escavadorToken}`,
          "User-Agent": "EGOS-OSINT/1.0"
        }
      });

      if (!response.ok) return null;
      return await response.json();
    } catch {
      return this.mockEscavador(nome);
    }
  }

  async queryJusbrasil(numeroProcesso: string): Promise<JusbrasilResult | null> {
    if (!this.jusbrasilToken) {
      console.warn("⚠️ JUSBRASIL_TOKEN não configurado");
      return this.mockJusbrasil(numeroProcesso);
    }

    try {
      const response = await fetch(
        `https://api.jusbrasil.com/v2/processos/${numeroProcesso}`,
        {
          headers: {
            "Authorization": `Bearer ${this.jusbrasilToken}`,
            "User-Agent": "EGOS-OSINT/1.0"
          }
        }
      );

      if (!response.ok) return null;
      return await response.json();
    } catch {
      return this.mockJusbrasil(numeroProcesso);
    }
  }

  async unifiedQuery(query: {
    cnpj?: string;
    nome?: string;
    processo?: string;
  }): Promise<{
    brasilIO?: BrasilIOResult;
    escavador?: EscavadorResult;
    jusbrasil?: JusbrasilResult;
    unified: {
      entidades: Array<{ tipo: string; nome: string; documento?: string }>;
      vinculos: Array<{ tipo: string; origem: string; destino: string; descricao: string }>;
      fontes: string[];
    };
  }> {
    const results: {
      brasilIO?: BrasilIOResult;
      escavador?: EscavadorResult;
      jusbrasil?: JusbrasilResult;
      unified: {
        entidades: Array<{ tipo: string; nome: string; documento?: string }>;
        vinculos: Array<{ tipo: string; origem: string; destino: string; descricao: string }>;
        fontes: string[];
      };
    } = {
      unified: {
        entidades: [],
        vinculos: [],
        fontes: []
      }
    };

    const promises: Promise<void>[] = [];

    if (query.cnpj) {
      promises.push(
        this.queryBrasilIO(query.cnpj).then(r => {
          if (r) {
            results.brasilIO = r;
            results.unified.fontes.push("brasil.io");
            this.normalizeBrasilIO(r, results.unified);
          }
        })
      );
    }

    if (query.nome) {
      promises.push(
        this.queryEscavador(query.nome).then(r => {
          if (r) {
            results.escavador = r;
            results.unified.fontes.push("escavador");
            this.normalizeEscavador(r, results.unified);
          }
        })
      );
    }

    if (query.processo) {
      promises.push(
        this.queryJusbrasil(query.processo).then(r => {
          if (r) {
            results.jusbrasil = r;
            results.unified.fontes.push("jusbrasil");
            this.normalizeJusbrasil(r, results.unified);
          }
        })
      );
    }

    await Promise.all(promises);

    return results;
  }

  private normalizeBrasilIO(data: BrasilIOResult, unified: typeof this.unifiedQuery extends (...args: any[]) => Promise<{ unified: infer U }> ? U : never): void {
    unified.entidades.push({
      tipo: "empresa",
      nome: data.razao_social || "",
      documento: data.cnpj
    });

    for (const socio of data.socios || []) {
      unified.entidades.push({
        tipo: "pessoa",
        nome: socio.nome
      });

      unified.vinculos.push({
        tipo: "sociedade",
        origem: socio.nome,
        destino: data.razao_social || "",
        descricao: socio.qualificacao
      });
    }
  }

  private normalizeEscavador(data: EscavadorResult, unified: any): void {
    if (data.pessoa) {
      unified.entidades.push({
        tipo: "pessoa",
        nome: data.pessoa.nome
      });

      for (const vinculo of data.pessoa.vinculos || []) {
        unified.vinculos.push({
          tipo: "vinculo_empresarial",
          origem: data.pessoa.nome,
          destino: vinculo.empresa,
          descricao: `${vinculo.cargo} (${vinculo.periodo})`
        });
      }
    }

    if (data.empresa) {
      unified.entidades.push({
        tipo: "empresa",
        nome: data.empresa.nome,
        documento: data.empresa.cnpj
      });
    }
  }

  private normalizeJusbrasil(data: JusbrasilResult, unified: any): void {
    if (data.processo) {
      for (const parte of data.processo.partes) {
        unified.entidades.push({
          tipo: parte.tipo.toLowerCase().includes("empresa") ? "empresa" : "pessoa",
          nome: parte.nome
        });

        unified.vinculos.push({
          tipo: "litigio",
          origem: parte.nome,
          destino: data.processo.numero,
          descricao: `${parte.tipo} em ${data.processo.classe}`
        });
      }
    }
  }

  // Mock data para desenvolvimento
  private mockBrasilIO(cnpj: string): BrasilIOResult {
    return {
      cnpj,
      razao_social: `EMPRESA ${cnpj.substring(0, 4)} LTDA`,
      nome_fantasia: "NOME FANTASIA",
      situacao: "ATIVA",
      data_abertura: "2020-01-01",
      endereco: {
        logradouro: "RUA EXEMPLO",
        numero: "123",
        bairro: "CENTRO",
        municipio: "BELO HORIZONTE",
        uf: "MG",
        cep: "30100-000"
      },
      atividade_principal: { code: "62.01-5-01", description: "Desenvolvimento de software" },
      socios: [
        { nome: "JOAO SILVA", qualificacao: "Sócio-Administrador" },
        { nome: "MARIA SOUZA", qualificacao: "Sócio" }
      ]
    };
  }

  private mockEscavador(nome: string): EscavadorResult {
    return {
      pessoa: {
        nome: nome.toUpperCase(),
        vinculos: [
          { empresa: "EMPRESA A LTDA", cargo: "Diretor", periodo: "2020-2024" },
          { empresa: "EMPRESA B SA", cargo: "Consultor", periodo: "2018-2020" }
        ]
      }
    };
  }

  private mockJusbrasil(numero: string): JusbrasilResult {
    return {
      processo: {
        numero,
        classe: "Ação Civil Pública",
        assunto: "LGPD - Dados Pessoais",
        foro: "Belo Horizonte",
        vara: "2ª Vara Cível",
        partes: [
          { nome: "AUTOR EXEMPLO", tipo: "Autor" },
          { nome: "REU EXEMPLO LTDA", tipo: "Réu" }
        ],
        movimentacoes: [
          { data: "2024-01-15", descricao: "Distribuição" },
          { data: "2024-02-01", descricao: "Conclusos para decisão" }
        ]
      }
    };
  }
}

// CLI interface
async function main() {
  const wrapper = new OSINTBrasilWrapper();
  const command = process.argv[2];

  switch (command) {
    case "cnpj": {
      const cnpj = process.argv[3]?.replace(/[^0-9]/g, "");
      if (!cnpj || cnpj.length !== 14) {
        console.log("Uso: bun osint-brasil-wrapper.ts cnpj 12345678000190");
        process.exit(1);
      }

      const result = await wrapper.queryBrasilIO(cnpj);
      console.log("\n🏢 Brasil.IO Resultado:");
      console.log(result);
      break;
    }

    case "nome": {
      const nome = process.argv[3];
      if (!nome) {
        console.log("Uso: bun osint-brasil-wrapper.ts nome 'João Silva'");
        process.exit(1);
      }

      const result = await wrapper.queryEscavador(nome);
      console.log("\n👤 Escavador Resultado:");
      console.log(result);
      break;
    }

    case "processo": {
      const processo = process.argv[3];
      if (!processo) {
        console.log("Uso: bun osint-brasil-wrapper.ts processo 1234567-12.2024.8.13.0000");
        process.exit(1);
      }

      const result = await wrapper.queryJusbrasil(processo);
      console.log("\n⚖️ Jusbrasil Resultado:");
      console.log(result);
      break;
    }

    case "unified": {
      const cnpj = process.argv[3]?.replace(/[^0-9]/g, "");
      const nome = process.argv[4];

      const result = await wrapper.unifiedQuery({ cnpj, nome });
      console.log("\n🔍 OSINT Unified Query:");
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    default:
      console.log(`
🔍 OSINT Brasil Wrapper — OSINT-006

Comandos:
  cnpj <cnpj>              Query Brasil.IO
  nome 'nome completo'     Query Escavador
  processo <numero>        Query Jusbrasil
  unified <cnpj> [nome]    Query unificada ( todas as fontes )

Exemplos:
  bun osint-brasil-wrapper.ts cnpj 11222333000144
  bun osint-brasil-wrapper.ts unified 11222333000144 "João Silva"

Variáveis de ambiente:
  BRASIL_IO_TOKEN, ESCAVADOR_TOKEN, JUSBRASIL_TOKEN
      `);
  }
}

if (import.meta.main) {
  main();
}

export { OSINTBrasilWrapper, type BrasilIOResult, type EscavadorResult, type JusbrasilResult };
