export const instant = false;

import Link from "next/link";

import { BackLink } from "@/components/BackLink";
import { SensorSeriesChart } from "@/components/telemetry/SensorSeriesChart";
import {
  OpsChartState,
  chartStatusFromPoints,
} from "@/components/telemetry/OpsChartState";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createTelemetryQueryPort } from "@/modules/telemetry-ingestion/infrastructure/processed-csv.adapter";

const WINDOWS = [
  { key: "120", label: "UDI 1–120", offset: 0, limit: 120 },
  { key: "500", label: "UDI 1–500", offset: 0, limit: 500 },
  { key: "tail", label: "Últimos 200 UDI", offset: 9800, limit: 200 },
] as const;

export default async function TelemetryPage({
  searchParams,
}: {
  searchParams: Promise<{ assetId?: string; window?: string }>;
}): Promise<React.JSX.Element> {
  const params = await searchParams;
  const assetId = params.assetId ?? "M14860";
  const windowKey = params.window ?? "120";
  const selected =
    WINDOWS.find((item) => item.key === windowKey) ?? WINDOWS[0];

  const port = createTelemetryQueryPort();
  let error: string | null = null;
  let points: Array<{
    udi: number;
    airTemp: number;
    processTemp: number;
    rpm: number;
    torque: number;
    toolWear: number;
  }> = [];

  try {
    // Context asset must exist; series uses UDI window from the real CSV.
    const asset = await port.getByProductId(assetId);
    if (!asset) {
      error = `El activo ${assetId} no está en el CSV procesado.`;
    } else {
      const rows = await port.seriesWindow({
        offset: selected.offset,
        limit: selected.limit,
      });
      points = rows.map((row) => ({
        udi: row.udi,
        airTemp: row.airTemp,
        processTemp: row.processTemp,
        rpm: row.rpm,
        torque: row.torque,
        toolWear: row.toolWear,
      }));
    }
  } catch (err) {
    error =
      err instanceof Error ? err.message : "No se pudo cargar la telemetría";
  }

  const status = error
    ? "empty"
    : chartStatusFromPoints(points.length, false);

  return (
    <div className="space-y-6">
      <BackLink
        href={`/assets/${encodeURIComponent(assetId)}`}
        label="Regresar al activo"
      />
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Telemetría</h1>
        <p className="text-sm text-[var(--fg-2)]">
          Explorador multi-serie sobre sensores reales del CSV procesado. El
          eje X es la secuencia UDI (no tiempo de reloj). Activo de contexto:{" "}
          <span className="font-mono">{assetId}</span>
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ventana UDI</CardTitle>
          <CardDescription>
            Los presets recortan el orden real del dataset. Sin marcas de
            tiempo inventadas.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {WINDOWS.map((item) => (
            <Link
              key={item.key}
              href={`/telemetry?assetId=${encodeURIComponent(assetId)}&window=${item.key}`}
              className={`rounded-md border px-3 py-1.5 text-xs ${
                item.key === selected.key
                  ? "border-[var(--line-strong)] bg-[var(--raised)] text-[var(--fg)]"
                  : "border-[var(--line)] text-[var(--fg-2)]"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Series de sensores</CardTitle>
          <CardDescription>
            Aire, proceso, RPM, torque y desgaste de herramienta del CSV
            procesado.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <OpsChartState status="empty" message={error} />
          ) : (
            <OpsChartState status={status}>
              <SensorSeriesChart data={points} />
            </OpsChartState>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
