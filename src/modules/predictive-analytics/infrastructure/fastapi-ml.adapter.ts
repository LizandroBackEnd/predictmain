import type {
  FailureRiskPort,
  PredictFeatures,
  PredictResult,
} from "@/modules/predictive-analytics/domain/failure-risk";

function resolveMlBaseUrl(): string {
  return process.env.ML_SERVICE_URL ?? "http://127.0.0.1:8000";
}

function normalizeProductType(value: string): "L" | "M" | "H" {
  if (value === "L" || value === "M" || value === "H") {
    return value;
  }
  throw new Error(`Unsupported product type for prediction: ${value}`);
}

export class FastApiMlAdapter implements FailureRiskPort {
  constructor(private readonly baseUrl: string = resolveMlBaseUrl()) {}

  async health(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: "GET",
        cache: "no-store",
      });
      if (!response.ok) {
        return false;
      }
      const body = (await response.json()) as { model_loaded?: boolean };
      return body.model_loaded === true;
    } catch {
      return false;
    }
  }

  async predict(features: PredictFeatures): Promise<PredictResult> {
    const response = await fetch(`${this.baseUrl}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({
        air_temperature_k: features.airTemp,
        process_temperature_k: features.processTemp,
        rotational_speed_rpm: features.rpm,
        torque_nm: features.torque,
        tool_wear_min: features.toolWear,
        product_type: normalizeProductType(features.productType),
      }),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`ML predict failed (${response.status}): ${detail}`);
    }

    const body = (await response.json()) as { failure_probability?: number };
    const probability = body.failure_probability;
    if (
      typeof probability !== "number" ||
      !Number.isFinite(probability) ||
      probability < 0 ||
      probability > 1
    ) {
      throw new Error("ML predict returned an invalid probability");
    }

    return { probability };
  }
}

export function createFailureRiskPort(baseUrl?: string): FailureRiskPort {
  return new FastApiMlAdapter(baseUrl ?? resolveMlBaseUrl());
}
