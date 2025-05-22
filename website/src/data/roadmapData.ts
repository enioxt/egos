// NOTE: Assuming Task interface is exported from Roadmap.tsx or moved later
export interface Task {
  id: string;
  titleKey: string; 
  status: 'Planned' | 'In Progress' | 'Completed' | 'Blocked' | 'DONE';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  subsystem?: string;
  phase?: string;
  description?: string; 
  detailsKey: string; 
  link?: string; 
}

export const roadmapTasks: Task[] = [
  // --- Phase 2a: Initial Framework & Standards --- (KOIOS Lead)
  { id: 'KOIOS-STD-STRUCT', titleKey: 'roadmap_tasks.koios_std_struct.title', status: 'DONE', priority: 'CRITICAL', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_std_struct.details' },
  { id: 'KOIOS-STD-COMMIT', titleKey: 'roadmap_tasks.koios_std_commit.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_std_commit.details' },
  { id: 'KOIOS-STD-PYTHON', titleKey: 'roadmap_tasks.koios_std_python.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_std_python.details' },
  { id: 'KOIOS-STD-LOGGING', titleKey: 'roadmap_tasks.koios_std_logging.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_std_logging.details' },
  { id: 'KOIOS-STD-DOCSTRINGS', titleKey: 'roadmap_tasks.koios_std_docstrings.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_std_docstrings.details' },
  { id: 'KOIOS-PRECOMMIT', titleKey: 'roadmap_tasks.koios_precommit.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_precommit.details' },
  { id: 'KOIOS-META-SCHEMA', titleKey: 'roadmap_tasks.koios_meta_schema.title', status: 'DONE', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_meta_schema.details' },
  { id: 'KOIOS-CURSOR-AGENT', titleKey: 'roadmap_tasks.koios_cursor_agent.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS/AI', phase: '2a', detailsKey: 'roadmap_tasks.koios_cursor_agent.details' },
  { id: 'KOIOS-RULES-CONSOLIDATE', titleKey: 'roadmap_tasks.koios_rules_consolidate.title', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_rules_consolidate.details' },
  { id: 'KOIOS-REFACTOR-META', titleKey: 'roadmap_tasks.koios_refactor_meta.title', status: 'In Progress', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_refactor_meta.details' },
  // --- Phase 2a: Documentation Tasks (Continued) ---
  { id: 'KOIOS-DOC-RU-01', titleKey: 'roadmap_tasks.koios_doc_ru_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_doc_ru_01.details' },
  { id: 'KOIOS-DOC-BP-FS-01', titleKey: 'roadmap_tasks.koios_doc_bp_fs_01.title', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_doc_bp_fs_01.details' },
  { id: 'KOIOS-LESSONS-01', titleKey: 'roadmap_tasks.koios_lessons_01.title', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_lessons_01.details' },
  { id: 'DOC-HTA-USAGE-01', titleKey: 'roadmap_tasks.doc_hta_usage_01.title', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS/NEXUS', phase: '2a', detailsKey: 'roadmap_tasks.doc_hta_usage_01.details' },
  { id: 'DOC-README-HTA-01', titleKey: 'roadmap_tasks.doc_readme_hta_01.title', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.doc_readme_hta_01.details' },
  { id: 'DOC-CONTRIB-AI-01', titleKey: 'roadmap_tasks.doc_contrib_ai_01.title', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.doc_contrib_ai_01.details' },
  { id: 'KOIOS-DOC-AUDIT-01', titleKey: 'roadmap_tasks.koios_doc_audit_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', detailsKey: 'roadmap_tasks.koios_doc_audit_01.details' },

  // --- 📈 Analysis & Insights (NEXUS Lead) ---
  { id: 'TASK-HTA-01', titleKey: 'roadmap_tasks.task_hta_01.title', status: 'DONE', priority: 'HIGH', subsystem: 'NEXUS/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.task_hta_01.details' },
  { id: 'HTA-02', titleKey: 'roadmap_tasks.hta_02.title', status: 'DONE', priority: 'MEDIUM', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.hta_02.details' },
  { id: 'HTA-DASH-01a', titleKey: 'roadmap_tasks.hta_dash_01a.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.hta_dash_01a.details' },
  { id: 'HTA-DASH-01b', titleKey: 'roadmap_tasks.hta_dash_01b.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.hta_dash_01b.details' },
  { id: 'HTA-REFINE-01', titleKey: 'roadmap_tasks.hta_refine_01.title', status: 'Planned', priority: 'LOW', subsystem: 'NEXUS/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.hta_refine_01.details' },

  // --- 🛡️ Security & Compliance (ETHIK Lead) ---
  { id: 'SEC-AUDIT-01', titleKey: 'roadmap_tasks.sec_audit_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'ETHIK/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.sec_audit_01.details' },

  // --- ✨ Orchestration & CI/CD (SPARC Lead) ---
  { id: 'SPARC-CI-SETUP-01', titleKey: 'roadmap_tasks.sparc_ci_setup_01.title', status: 'DONE', priority: 'CRITICAL', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.sparc_ci_setup_01.details' },
  { id: 'SPARC-CI-TEST-01', titleKey: 'roadmap_tasks.sparc_ci_test_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.sparc_ci_test_01.details' },
  { id: 'SPARC-CD-SETUP-01', titleKey: 'roadmap_tasks.sparc_cd_setup_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'SPARC/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.sparc_cd_setup_01.details' },
  { id: 'SPARC-MONITOR-01', titleKey: 'roadmap_tasks.sparc_monitor_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'SPARC/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.sparc_monitor_01.details' },

  // --- 💻 Environment & Compatibility (HARMONY Lead) ---
  { id: 'HARMONY-DEP-MGMT-01', titleKey: 'roadmap_tasks.harmony_dep_mgmt_01.title', status: 'DONE', priority: 'CRITICAL', subsystem: 'HARMONY/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.harmony_dep_mgmt_01.details' },
  { id: 'HARMONY-WIN-COMPAT-01', titleKey: 'roadmap_tasks.harmony_win_compat_01.title', status: 'DONE', priority: 'HIGH', subsystem: 'HARMONY', phase: '2', detailsKey: 'roadmap_tasks.harmony_win_compat_01.details' },
  { id: 'HARMONY-CONTAINER-01', titleKey: 'roadmap_tasks.harmony_container_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'HARMONY/SPARC', phase: '2', detailsKey: 'roadmap_tasks.harmony_container_01.details' },

  // --- 🎨 UI & User Experience (CORUJA Lead) ---
  { id: 'CORUJA-UI-LIB-01', titleKey: 'roadmap_tasks.coruja_ui_lib_01.title', status: 'DONE', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.coruja_ui_lib_01.details' },
  { id: 'CORUJA-DESIGN-SYS-01', titleKey: 'roadmap_tasks.coruja_design_sys_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.coruja_design_sys_01.details' },
  { id: 'CORUJA-ACCESSIBILITY-01', titleKey: 'roadmap_tasks.coruja_accessibility_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/ETHIK', phase: '2', detailsKey: 'roadmap_tasks.coruja_accessibility_01.details' },
  { id: 'CORUJA-WEB-INIT-01', titleKey: 'roadmap_tasks.coruja_web_init_01.title', status: 'DONE', priority: 'CRITICAL', subsystem: 'CORUJA/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.coruja_web_init_01.details' },
  { id: 'CORUJA-WEB-FOOTER-LINKS-01', titleKey: 'roadmap_tasks.coruja_web_footer_links_01.title', status: 'DONE', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.coruja_web_footer_links_01.details' },
  { id: 'CORUJA-WEB-ROADMAP-01', titleKey: 'roadmap_tasks.coruja_web_roadmap_01.title', status: 'In Progress', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.coruja_web_roadmap_01.details', link: 'https://github.com/enioxt/egos/blob/main/website/src/components/Roadmap.tsx' },
  { id: 'CORUJA-WEB-CONTRIB-MODAL-01', titleKey: 'roadmap_tasks.coruja_web_contrib_modal_01.title', status: 'In Progress', priority: 'HIGH', subsystem: 'CORUJA/KOIOS/AI', phase: '2', detailsKey: 'roadmap_tasks.coruja_web_contrib_modal_01.details', link: 'https://github.com/enioxt/egos/blob/main/website/src/components/Roadmap.tsx#L113' },
  { id: 'CORUJA-WEB-LLM-API-01', titleKey: 'roadmap_tasks.coruja_web_llm_api_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'MYCELIUM/AI', phase: '3', detailsKey: 'roadmap_tasks.coruja_web_llm_api_01.details' },
  { id: 'CORUJA-WEB-LLM-UI-01', titleKey: 'roadmap_tasks.coruja_web_llm_ui_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'CORUJA/AI', phase: '3', detailsKey: 'roadmap_tasks.coruja_web_llm_ui_01.details' },

  // --- 🕸️ Communication & APIs (MYCELIUM Lead) ---
  { id: 'MYCELIUM-API-DESIGN-01', titleKey: 'roadmap_tasks.mycelium_api_design_01.title', status: 'DONE', priority: 'HIGH', subsystem: 'MYCELIUM/KOIOS', phase: '2', detailsKey: 'roadmap_tasks.mycelium_api_design_01.details' },
  { id: 'MYCELIUM-INTER-SVC-COMM-01', titleKey: 'roadmap_tasks.mycelium_inter_svc_comm_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'MYCELIUM/SPARC', phase: '2', detailsKey: 'roadmap_tasks.mycelium_inter_svc_comm_01.details' },

  // --- ⏳ State & Persistence (CRONOS Lead) ---
  { id: 'CRONOS-DB-SELECT-01', titleKey: 'roadmap_tasks.cronos_db_select_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'CRONOS/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.cronos_db_select_01.details' },
  { id: 'CRONOS-ORM-SETUP-01', titleKey: 'roadmap_tasks.cronos_orm_setup_01.title', status: 'Planned', priority: 'HIGH', subsystem: 'CRONOS/HARMONY', phase: '2', detailsKey: 'roadmap_tasks.cronos_orm_setup_01.details' },
  { id: 'CRONOS-BACKUP-STRAT-01', titleKey: 'roadmap_tasks.cronos_backup_strat_01.title', status: 'Planned', priority: 'MEDIUM', subsystem: 'CRONOS/SPARC', phase: '2', detailsKey: 'roadmap_tasks.cronos_backup_strat_01.details' },
];
