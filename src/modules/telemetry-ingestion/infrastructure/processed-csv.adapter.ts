import { readFile } from "node:fs/promises";
import path from "node:path";

import type {
  TelemetryQueryPort,
  TelemetryRow,
} from "@/modules/telemetry-ingestion/domain/telemetry-row";

const DEFAULT_RELATIVE_CSV = path.join(
  "data",
  "processed",
  "ai4i2020_outlier_analyzed.csv",
);

let cachedRows: TelemetryRow[] | null = null;
let cachedPath: string | null = null;

function resolveCsvPath(explicit?: string): string {
  if (explicit) {
    return explicit;
  }
  if (process.env.AI4I_PROCESSED_CSV) {
    return process.env.AI4I_PROCESSED_CSV;
  }
  return path.join(process.cwd(), DEFAULT_RELATIVE_CSV);
}

function parseCsvLine(line: string): string[] {
  return line.split(",").map((cell) => cell.trim());
}

function toNumber(value: string, field: string): number {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    throw new Error(`Invalid numeric value for ${field}: ${value}`);
  }
  return n;
}

function mapRow(headers: string[], cells: string[]): TelemetryRow {
  const get = (name: string): string => {
    const idx = headers.indexOf(name);
    if (idx < 0 || idx >= cells.length) {
      throw new Error(`Missing column ${name}`);
    }
    return cells[idx] ?? "";
  };

  const failure = toNumber(get("Machine failure"), "Machine failure");
  if (failure !== 0 && failure !== 1) {
    throw new Error(`Invalid Machine failure value: ${failure}`);
  }

  return {
    udi: toNumber(get("UDI"), "UDI"),
    productId: get("Product ID"),
    type: get("Type"),
    airTemp: toNumber(get("Air temperature [K]"), "Air temperature [K]"),
    processTemp: toNumber(
      get("Process temperature [K]"),
      "Process temperature [K]",
    ),
    rpm: toNumber(get("Rotational speed [rpm]"), "Rotational speed [rpm]"),
    torque: toNumber(get("Torque [Nm]"), "Torque [Nm]"),
    toolWear: toNumber(get("Tool wear [min]"), "Tool wear [min]"),
    machineFailure: failure,
  };
}

async function loadRows(csvPath: string): Promise<TelemetryRow[]> {
  if (cachedRows && cachedPath === csvPath) {
    return cachedRows;
  }

  let raw: string;
  try {
    raw = await readFile(csvPath, "utf8");
  } catch {
    throw new Error(`Processed CSV not found: ${csvPath}`);
  }

  const lines = raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines.length < 2) {
    cachedRows = [];
    cachedPath = csvPath;
    return cachedRows;
  }

  const headers = parseCsvLine(lines[0] ?? "");
  const rows: TelemetryRow[] = [];
  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line) {
      continue;
    }
    rows.push(mapRow(headers, parseCsvLine(line)));
  }

  cachedRows = rows;
  cachedPath = csvPath;
  return rows;
}

/** Test helper: clears module cache between Bun tests. */
export function clearProcessedCsvCache(): void {
  cachedRows = null;
  cachedPath = null;
}

export class ProcessedCsvTelemetryAdapter implements TelemetryQueryPort {
  constructor(private readonly csvPath: string = resolveCsvPath()) {}

  async getByProductId(productId: string): Promise<TelemetryRow | null> {
    const rows = await loadRows(this.csvPath);
    return rows.find((row) => row.productId === productId) ?? null;
  }

  async getByUdi(udi: number): Promise<TelemetryRow | null> {
    const rows = await loadRows(this.csvPath);
    return rows.find((row) => row.udi === udi) ?? null;
  }

  async listSlice(opts: {
    offset: number;
    limit: number;
  }): Promise<TelemetryRow[]> {
    const rows = await loadRows(this.csvPath);
    const start = Math.max(0, opts.offset);
    return rows.slice(start, start + Math.max(0, opts.limit));
  }

  async seriesWindow(opts: {
    offset: number;
    limit: number;
  }): Promise<TelemetryRow[]> {
    return this.listSlice(opts);
  }
}

export function createTelemetryQueryPort(
  csvPath?: string,
): TelemetryQueryPort {
  return new ProcessedCsvTelemetryAdapter(
    csvPath ? csvPath : resolveCsvPath(),
  );
}
