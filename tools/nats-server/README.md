@references:
  - tools/nats-server/README.md

# EGOS NATS Server

## Visão Geral

Este componente fornece o servidor NATS necessário para a integração de dados em tempo real do Dashboard EGOS. O NATS (Neural Autonomic Transport System) é um sistema de mensagens de alto desempenho que permite a comunicação assíncrona entre os diversos componentes do ecossistema EGOS.

## Alinhamento com Princípios EGOS

Este componente implementa os seguintes princípios do Master Quantum Prompt (MQP v9.0):

* **Conscious Modularity**: O servidor NATS atua como um barramento de mensagens independente que facilita a comunicação entre módulos sem criar dependências diretas.
* **Systemic Cartography**: Fornece uma infraestrutura clara para o mapeamento e rastreamento de fluxos de dados em tempo real através do sistema.
* **Integrated Ethics**: Suporta a transmissão de metadados éticos e contextuais junto com as mensagens principais.

## Integração com o Dashboard

Este servidor NATS é referenciado pelo `MyceliumClient` no dashboard EGOS para estabelecer conexões em tempo real. Por padrão, o servidor escuta em:

* Endereço principal: `nats://localhost:4222` (para conexões de clientes)
* Monitoramento HTTP: `http://localhost:8222` (para estatísticas e monitoramento)

## Uso

Para iniciar o servidor NATS:

1. Abra um terminal PowerShell
2. Navegue até este diretório: `cd C:\EGOS\tools\nats-server`
3. Execute o script: `.\download-and-run-nats.ps1`
4. Mantenha o terminal aberto enquanto o dashboard estiver em uso

## Referências

* [Estratégia de Integração de Dados em Tempo Real do Dashboard](file:///C:/EGOS/docs/planning/Dashboard_Realtime_Data_Strategy.md)
* [EGOS Roadmap - Seção de Evolução do Dashboard](file:///C:/EGOS/ROADMAP.md)
* [Documentação do Dashboard](file:///C:/EGOS/apps/dashboard/README.md)

## Logs

Os logs do servidor são armazenados no diretório `logs/` e podem ser úteis para diagnóstico de problemas de conexão.

---

*Este componente é parte da infraestrutura de integração em tempo real do EGOS, conforme definido na tarefa DBP-P1.1.1 do roadmap.*