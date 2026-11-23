export const instant = false;

import Link from "next/link";

import {
  OperationsPagination,
  PAGE_SIZE,
} from "@/app/(dashboard)/operations/_components/OperationsPagination";
import { OperationsQueue } from "@/app/(dashboard)/operations/_components/OperationsQueue";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  severityFromFailure,
  type Severity,
} from "@/modules/telemetry-ingestion/domain/telemetry-row";
import { createTelemetryQueryPort } from "@/modules/telemetry-ingestion/infrastructure/processed-csv.adapter";

const SEVERITY_LABELS = {
  all: "todas",
  critical: "crítica",
  warning: "advertencia",
  ok: "normal",
} as const;

function parsePage(value: string | undefined): number {
  const parsed = Number.parseInt(value ?? "1", 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return 1;
  }
  return parsed;
}

export default async function OperationsPage({
  searchParams,
}: {
  searchParams: Promise<{ severity?: string; page?: string }>;
}): Promise<React.JSX.Element> {
  const params = await searchParams;
  const severityFilter = params.severity as Severity | "all" | undefined;
  const page = parsePage(params.page);

  let error: string | null = null;
  let rows: Awaited<
    ReturnType<ReturnType<typeof createTelemetryQueryPort>["listSlice"]>
  > = [];

  try {
    const port = createTelemetryQueryPort();
    const all = await port.listSlice({ offset: 0, limit: 10000 });
    const failures = all.filter((row) => row.machineFailure === 1);
    const healthy = all.filter((row) => row.machineFailure === 0);
    rows = [...failures, ...healthy];
  } catch (err) {
    error =
      err instanceof Error
        ? err.message
        : "No se pudo cargar el CSV procesado";
  }

  const critical = rows.filter((r) => r.machineFailure === 1).length;
  const ok = rows.length - critical;

  const filtered = rows
    .map((row) => ({
      productId: row.productId,
      udi: row.udi,
      type: row.type,
      severity: severityFromFailure(row.machineFailure),
      airTemp: row.airTemp,
      rpm: row.rpm,
      torque: row.torque,
    }))
    .filter((item) =>
      !severityFilter || severityFilter === "all"
        ? true
        : item.severity === severityFilter,
    );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageItems = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Operación</h1>
        <p className="text-sm text-[var(--fg-2)]">
          Cola de riesgo con filas reales del CSV AI4I (etiqueta{" "}
          <code>Machine failure</code>).
        </p>
      </div>

      {error ? (
        <Card>
          <CardHeader>
            <CardTitle>Fuente no disponible</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card>
              <CardHeader>
                <CardDescription>Muestras en cola</CardDescription>
                <CardTitle className="text-2xl">{rows.length}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Fallos etiquetados</CardDescription>
                <CardTitle className="text-2xl text-[var(--crit)]">
                  {critical}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Muestras normales</CardDescription>
                <CardTitle className="text-2xl text-[var(--ok)]">{ok}</CardTitle>
              </CardHeader>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle>Filtro de severidad</CardTitle>
                <CardDescription>
                  Derivado de las etiquetas reales <code>Machine failure</code>{" "}
                  del CSV. {PAGE_SIZE} filas por página.
                </CardDescription>
              </div>
              <div className="flex gap-2">
                {(["all", "critical", "ok"] as const).map((value) => (
                  <Link
                    key={value}
                    href={
                      value === "all"
                        ? "/operations"
                        : `/operations?severity=${value}`
                    }
                  >
                    <Badge
                      variant={
                        value === "critical"
                          ? "critical"
                          : value === "ok"
                            ? "ok"
                            : "default"
                      }
                    >
                      {SEVERITY_LABELS[value]}
                    </Badge>
                  </Link>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <OperationsQueue items={pageItems} />
              <OperationsPagination
                page={currentPage}
                totalItems={filtered.length}
                severity={severityFilter}
              />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
