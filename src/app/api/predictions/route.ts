import { NextResponse } from "next/server";

import { createFailureRiskPort } from "@/modules/predictive-analytics/infrastructure/fastapi-ml.adapter";

interface PredictBody {
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
  productType: string;
}

export async function GET(): Promise<NextResponse> {
  const port = createFailureRiskPort();
  const healthy = await port.health();
  return NextResponse.json({ healthy });
}

export async function POST(request: Request): Promise<NextResponse> {
  let body: PredictBody;
  try {
    body = (await request.json()) as PredictBody;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const required = [
    "airTemp",
    "processTemp",
    "rpm",
    "torque",
    "toolWear",
    "productType",
  ] as const;
  for (const key of required) {
    if (body[key] === undefined || body[key] === null) {
      return NextResponse.json(
        { error: `Missing field: ${key}` },
        { status: 400 },
      );
    }
  }

  try {
    const port = createFailureRiskPort();
    const result = await port.predict(body);
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Prediction failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
