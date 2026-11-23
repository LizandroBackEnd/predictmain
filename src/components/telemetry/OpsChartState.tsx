import type { JSX, ReactNode } from "react";

export type ChartStatus = "loading" | "empty" | "incomplete" | "ready";

export function OpsChartState({
  status,
  children,
  message,
}: {
  status: ChartStatus;
  children?: ReactNode;
  message?: string;
}): JSX.Element {
  if (status === "ready") {
    return <>{children}</>;
  }

  const defaults: Record<Exclude<ChartStatus, "ready">, string> = {
    loading: "Cargando datos del gráfico…",
    empty: "No hay puntos disponibles para esta ventana.",
    incomplete: "Lectura incompleta — faltan campos de sensores.",
  };

  return (
    <div className="flex aspect-video items-center justify-center rounded-lg border border-dashed border-[var(--line)] bg-[var(--raised)] px-6 text-center text-sm text-[var(--fg-2)]">
      {message ?? defaults[status]}
    </div>
  );
}

export function chartStatusFromPoints(
  count: number,
  incomplete = false,
): ChartStatus {
  if (incomplete) {
    return "incomplete";
  }
  if (count <= 0) {
    return "empty";
  }
  return "ready";
}
