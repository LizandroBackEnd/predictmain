import { describe, expect, test, beforeEach } from "bun:test";
import path from "node:path";

import {
  ProcessedCsvTelemetryAdapter,
  clearProcessedCsvCache,
} from "@/modules/telemetry-ingestion/infrastructure/processed-csv.adapter";

const csvPath = path.join(
  process.cwd(),
  "data/processed/ai4i2020_outlier_analyzed.csv",
);

describe("ProcessedCsvTelemetryAdapter", () => {
  beforeEach(() => {
    clearProcessedCsvCache();
  });

  test("returns real M14860 sensors matching the processed CSV", async () => {
    const adapter = new ProcessedCsvTelemetryAdapter(csvPath);
    const row = await adapter.getByProductId("M14860");
    expect(row).not.toBeNull();
    expect(row?.udi).toBe(1);
    expect(row?.type).toBe("M");
    expect(row?.airTemp).toBe(298.1);
    expect(row?.processTemp).toBe(308.6);
    expect(row?.rpm).toBe(1551);
    expect(row?.torque).toBe(42.8);
    expect(row?.toolWear).toBe(0);
    expect(row?.machineFailure).toBe(0);
  });

  test("returns null for unknown product ids without inventing rows", async () => {
    const adapter = new ProcessedCsvTelemetryAdapter(csvPath);
    const row = await adapter.getByProductId("FR-204");
    expect(row).toBeNull();
  });
});
