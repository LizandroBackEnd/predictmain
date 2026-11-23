export type ProductType = string;

export interface TelemetryRow {
  udi: number;
  productId: string;
  type: ProductType;
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
  machineFailure: 0 | 1;
}

export type Severity = "critical" | "warning" | "ok";

export function severityFromFailure(machineFailure: 0 | 1): Severity {
  return machineFailure === 1 ? "critical" : "ok";
}

export function severityFromProbability(probability: number): Severity {
  if (probability >= 0.7) {
    return "critical";
  }
  if (probability >= 0.35) {
    return "warning";
  }
  return "ok";
}

export interface TelemetryQueryPort {
  getByProductId(productId: string): Promise<TelemetryRow | null>;
  getByUdi(udi: number): Promise<TelemetryRow | null>;
  listSlice(opts: { offset: number; limit: number }): Promise<TelemetryRow[]>;
  seriesWindow(opts: {
    offset: number;
    limit: number;
  }): Promise<TelemetryRow[]>;
}
