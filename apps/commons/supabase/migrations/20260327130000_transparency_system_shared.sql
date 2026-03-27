-- Transparency System Tables (Shared)
-- Created: 2026-03-27
-- Purpose: Centralized timeline, telemetry, and observability for EGOS ecosystem
-- This migration syncs to all projects via commons package
-- Note: If forja/supabase already has this, it will be skipped

-- ═══ Timeline de Relatórios (Central) ═══
CREATE TABLE IF NOT EXISTS transparency_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    system VARCHAR(50) NOT NULL,
    agent VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    triggered_by VARCHAR(20) NOT NULL,
    output_url TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══ Métricas (Time-Series) ═══
CREATE TABLE IF NOT EXISTS transparency_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    system VARCHAR(50) NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),
    dimensions JSONB,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══ Logs de Observabilidade ═══
CREATE TABLE IF NOT EXISTS transparency_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    system VARCHAR(50) NOT NULL,
    agent VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══ Alertas (Real-time Notifications) ═══
CREATE TABLE IF NOT EXISTS transparency_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    message TEXT,
    severity VARCHAR(20) NOT NULL,
    system VARCHAR(50) NOT NULL,
    report_id UUID REFERENCES transparency_reports(id) ON DELETE CASCADE,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══ Índices ═══
CREATE INDEX IF NOT EXISTS idx_reports_system_status ON transparency_reports(system, status);
CREATE INDEX IF NOT EXISTS idx_reports_started_at ON transparency_reports(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_name_system_time ON transparency_metrics(metric_name, system, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_trace_id ON transparency_logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity_triggered ON transparency_alerts(severity, triggered_at DESC);

-- ═══ RLS ═══
ALTER TABLE transparency_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE transparency_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE transparency_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE transparency_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "transparency_reports_read" ON transparency_reports FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "transparency_reports_write" ON transparency_reports FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "transparency_metrics_read" ON transparency_metrics FOR SELECT USING (true);
CREATE POLICY "transparency_metrics_write" ON transparency_metrics FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "transparency_logs_read" ON transparency_logs FOR SELECT USING (true);
CREATE POLICY "transparency_logs_write" ON transparency_logs FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "transparency_alerts_read" ON transparency_alerts FOR SELECT USING (true);
CREATE POLICY "transparency_alerts_write" ON transparency_alerts FOR INSERT WITH CHECK (auth.role() = 'authenticated');
