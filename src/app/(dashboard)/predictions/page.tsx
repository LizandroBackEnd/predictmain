export const instant = false;

import Link from "next/link";

import { ActionStrip } from "@/app/(dashboard)/predictions/_components/ActionStrip";
import { BackLink } from "@/components/BackLink";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { OpsChartState } from "@/components/telemetry/OpsChartState";
import { createFailureRiskPort } from "@/modules/predictive-analytics/infrastructure/fastapi-ml.adapter";
import { severityFromProbability } from "@/modules/telemetry-ingestion/domain/telemetry-row";
import { createTelemetryQueryPort } from "@/modules/telemetry-ingestion/infrastructure/processed-csv.adapter";

const SEVERITY_LABELS = {
  critical: "crítica",
  warning: "advertencia",
  ok: "normal",
} as const;

export default async function PredictionsPage({
  searchParams,
}: {
  searchParams: Promise<{ assetId?: string }>;
}): Promise<React.JSX.Element> {
  const params = await searchParams;
  const assetId = params.assetId ?? "M14860";

  const telemetry = createTelemetryQueryPort();
  const riskPort = createFailureRiskPort();

  let sourceError: string | null = null;
  let predictError: string | null = null;
  let probability: number | null = null;
  let labelFailure: 0 | 1 | null = null;
  let healthy = false;

  try {
    const row = await telemetry.getByProductId(assetId);
    if (!row) {
      sourceError = `El activo ${assetId} no está en el CSV procesado.`;
    } else {
      labelFailure = row.machineFailure;
      healthy = await riskPort.health();
      if (!healthy) {
        predictError =
          "Servicio ML no disponible. Inicie FastAPI (`python dev.py` o `bun run dev:ml`) con modelo.joblib presente.";
      } else {
        try {
          const result = await riskPort.predict({
            airTemp: row.airTemp,
            processTemp: row.processTemp,
            rpm: row.rpm,
            torque: row.torque,
            toolWear: row.toolWear,
            productType: row.type,
          });
          probability = result.probability;
        } catch (err) {
          predictError =
            err instanceof Error
              ? err.message
              : "Falló la solicitud de predicción";
        }
      }
    }
  } catch (err) {
    sourceError =
      err instanceof Error ? err.message : "No se pudo cargar el CSV";
  }

  const severity =
    probability === null ? null : severityFromProbability(probability);

  return (
    <div className="space-y-6">
      <BackLink
        href={`/assets/${encodeURIComponent(assetId)}`}
        label="Regresar al activo"
      />
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Riesgo de falla
        </h1>
        <p className="text-sm text-[var(--fg-2)]">
          Puntaje del modelo HU-08 <code>modelo.joblib</code> vía FastAPI para{" "}
          <span className="font-mono">{assetId}</span>.
        </p>
      </div>

      {sourceError ? (
        <Card>
          <CardHeader>
            <CardTitle>Fuente no disponible</CardTitle>
            <CardDescription>{sourceError}</CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardDescription>Probabilidad del modelo</CardDescription>
                <CardTitle className="text-3xl font-mono">
                  {probability === null
                    ? "—"
                    : `${(probability * 100).toFixed(1)}%`}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {severity ? (
                  <Badge
                    variant={
                      severity === "critical"
                        ? "critical"
                        : severity === "warning"
                          ? "warning"
                          : "ok"
                    }
                  >
                    {SEVERITY_LABELS[severity]}
                  </Badge>
                ) : (
                  <span className="text-xs text-[var(--fg-3)]">
                    No disponible
                  </span>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>
                  Etiqueta CSV (Machine failure)
                </CardDescription>
                <CardTitle className="text-3xl font-mono">
                  {labelFailure === null ? "—" : labelFailure}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-[var(--fg-3)]">
                Etiqueta real del dataset procesado — no inventada.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Servicio ML</CardDescription>
                <CardTitle className="text-xl">
                  {healthy ? "En línea" : "Caído"}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-[var(--fg-3)]">
                <Link
                  href="/api/predictions"
                  className="text-[var(--risk)] hover:underline"
                >
                  Ver salud del proxy /api/predictions
                </Link>
              </CardContent>
            </Card>
          </div>

          {predictError ? (
            <OpsChartState status="empty" message={predictError} />
          ) : null}

          <ActionStrip severity={severity} probability={probability} />
        </>
      )}
    </div>
  );
}
