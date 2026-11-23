import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { TelemetryRow } from "@/modules/telemetry-ingestion/domain/telemetry-row";

function isFiniteNumber(value: number): boolean {
  return Number.isFinite(value);
}

export function ReadingsPanel({
  row,
}: {
  row: TelemetryRow;
}): React.JSX.Element {
  const readings: Array<{
    key: string;
    label: string;
    value: number;
    unit: string;
  }> = [
    { key: "air", label: "Temp. del aire", value: row.airTemp, unit: "K" },
    {
      key: "process",
      label: "Temp. del proceso",
      value: row.processTemp,
      unit: "K",
    },
    { key: "rpm", label: "Velocidad de rotación", value: row.rpm, unit: "rpm" },
    { key: "torque", label: "Torque", value: row.torque, unit: "Nm" },
    {
      key: "wear",
      label: "Desgaste de herramienta",
      value: row.toolWear,
      unit: "min",
    },
  ];

  const incomplete = readings.some((item) => !isFiniteNumber(item.value));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Últimas lecturas</CardTitle>
        <CardDescription>
          Valores de la fila del CSV procesado para {row.productId}
          {incomplete ? " · campos incompletos marcados" : ""}.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {readings.map((item) => {
            const ok = isFiniteNumber(item.value);
            return (
              <div
                key={item.key}
                className="rounded-md border border-[var(--line)] bg-[var(--raised)] p-3"
              >
                <div className="text-xs text-[var(--fg-3)]">{item.label}</div>
                <div className="mt-1 font-mono text-lg">
                  {ok ? item.value : "—"}
                  <span className="ml-1 text-xs text-[var(--fg-3)]">
                    {item.unit}
                  </span>
                </div>
                {!ok ? (
                  <div className="mt-1 text-[11px] text-[var(--warn)]">
                    Incompleto
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
