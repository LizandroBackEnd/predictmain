export const instant = false;

import Link from "next/link";
import { notFound } from "next/navigation";

import { ReadingsPanel } from "@/app/(dashboard)/assets/[id]/_components/ReadingsPanel";
import { BackLink } from "@/components/BackLink";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { severityFromFailure } from "@/modules/telemetry-ingestion/domain/telemetry-row";
import { createTelemetryQueryPort } from "@/modules/telemetry-ingestion/infrastructure/processed-csv.adapter";

export default async function AssetDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<React.JSX.Element> {
  const { id } = await params;
  const productId = decodeURIComponent(id);
  const port = createTelemetryQueryPort();

  let row;
  try {
    row = await port.getByProductId(productId);
  } catch (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Fuente no disponible</CardTitle>
          <CardDescription>
            {error instanceof Error
              ? error.message
              : "No se pudo leer el CSV"}
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!row) {
    notFound();
  }

  const severity = severityFromFailure(row.machineFailure);
  const severityLabel =
    severity === "critical"
      ? "crítica"
      : severity === "warning"
        ? "advertencia"
        : "normal";

  return (
    <div className="space-y-6">
      <BackLink href="/operations" label="Regresar a operación" />
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.14em] text-[var(--fg-3)]">
            Detalle del activo
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {row.productId}
          </h1>
          <p className="text-sm text-[var(--fg-2)]">
            UDI {row.udi} · Tipo {row.type}
          </p>
        </div>
        <Badge
          variant={
            severity === "critical"
              ? "critical"
              : severity === "warning"
                ? "warning"
                : "ok"
          }
        >
          {severityLabel}
        </Badge>
      </div>

      <ReadingsPanel row={row} />

      <Card>
        <CardHeader>
          <CardTitle>Siguientes acciones</CardTitle>
          <CardDescription>
            Los enlaces conservan el mismo Product ID real.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link
            href={`/telemetry?assetId=${encodeURIComponent(row.productId)}`}
            className="inline-flex h-9 items-center rounded-md bg-[var(--btn-bg)] px-4 text-sm font-medium text-[var(--btn-fg)]"
          >
            Abrir telemetría
          </Link>
          <Link
            href={`/predictions?assetId=${encodeURIComponent(row.productId)}`}
            className="inline-flex h-9 items-center rounded-md border border-[var(--line)] px-4 text-sm font-medium text-[var(--fg)]"
          >
            Abrir riesgo de falla
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
