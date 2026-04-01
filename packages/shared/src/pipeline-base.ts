/**
 * PipelineBase — Universal ETL pipeline base class with IngestionRun tracking.
 * Ported from br-acc/etl/src/bracc_etl/base.py (BRACC-003).
 *
 * Transport-agnostic: subclasses inject a `runStore` to persist IngestionRun
 * state (Neo4j, Supabase, or no-op). Guard Brasil PII hook included.
 */

export type RunStatus = "running" | "loaded" | "quality_fail";

export interface IngestionRun {
  run_id: string;
  source_id: string;
  status: RunStatus;
  started_at: string;
  finished_at?: string;
  error?: string;
  rows_in?: number;
  rows_loaded?: number;
}

/** Minimal interface for persisting IngestionRun records. */
export interface RunStore {
  upsert(run: IngestionRun): Promise<void>;
}

/** No-op store — useful for testing or when persistence isn't needed. */
export const noopRunStore: RunStore = {
  async upsert() {},
};

export interface PipelineOptions {
  /** Data directory for raw files (default: ./data). */
  dataDir?: string;
  /** Row limit — useful for dev/test runs. */
  limit?: number;
  /** Chunk size for bulk operations. */
  chunkSize?: number;
  /** Run store for IngestionRun persistence. */
  runStore?: RunStore;
}

export abstract class Pipeline {
  abstract readonly name: string;
  abstract readonly sourceId: string;

  protected readonly dataDir: string;
  protected readonly limit?: number;
  protected readonly chunkSize: number;
  protected readonly runStore: RunStore;
  protected readonly runId: string;

  constructor(opts: PipelineOptions = {}) {
    this.dataDir = opts.dataDir ?? "./data";
    this.limit = opts.limit;
    this.chunkSize = opts.chunkSize ?? 50_000;
    this.runStore = opts.runStore ?? noopRunStore;
    const ts = new Date().toISOString().replace(/[-:T.]/g, "").slice(0, 14);
    this.runId = `${this.constructor.name}_${ts}`;
  }

  /** Download raw data from source. */
  abstract extract(): Promise<void>;

  /** Normalize, deduplicate, and prepare data for loading. */
  abstract transform(): Promise<void>;

  /** Load transformed data into the target store. */
  abstract load(): Promise<void>;

  /**
   * Execute the full ETL pipeline.
   * Persists IngestionRun status at each phase transition.
   */
  async run(): Promise<void> {
    const startedAt = new Date().toISOString();
    await this._upsertRun({ status: "running", started_at: startedAt });

    try {
      console.info(`[${this.name}] Starting extraction...`);
      await this.extract();

      console.info(`[${this.name}] Starting transformation...`);
      await this.transform();

      console.info(`[${this.name}] Running Guard Brasil check...`);
      await this._guardCheck();

      console.info(`[${this.name}] Starting load...`);
      await this.load();

      const finishedAt = new Date().toISOString();
      await this._upsertRun({ status: "loaded", started_at: startedAt, finished_at: finishedAt });
      console.info(`[${this.name}] Pipeline complete.`);
    } catch (err) {
      const finishedAt = new Date().toISOString();
      const error = (err instanceof Error ? err.message : String(err)).slice(0, 1000);
      await this._upsertRun({
        status: "quality_fail",
        started_at: startedAt,
        finished_at: finishedAt,
        error,
      });
      throw err;
    }
  }

  // ── Guard Brasil integration ──────────────────────────────────────────────

  /**
   * Column names in transformed data that may contain free text / PII.
   * Override in subclass to enable automatic Guard Brasil scanning.
   */
  protected guardTextColumns: string[] = [];

  /**
   * If true, block load when PII is detected. Default: mask and continue.
   */
  protected guardStrict = false;

  /**
   * Override to implement PII scanning. Called by run() before load().
   * Default implementation is a no-op (Guard Brasil is an optional dep).
   */
  protected async _guardCheck(): Promise<void> {
    if (this.guardTextColumns.length === 0) return;
    // Subclasses can override to integrate guard-brasil npm package:
    // const { scan } = await import('@egosbr/guard-brasil');
    // ...
    console.debug(`[${this.name}] Guard check: no implementation — override _guardCheck()`);
  }

  // ── Internal ──────────────────────────────────────────────────────────────

  private async _upsertRun(
    fields: Omit<IngestionRun, "run_id" | "source_id">
  ): Promise<void> {
    try {
      await this.runStore.upsert({
        run_id: this.runId,
        source_id: this.sourceId,
        ...fields,
      });
    } catch (err) {
      console.warn(`[${this.name}] failed to persist IngestionRun: ${(err as Error).message}`);
    }
  }
}
