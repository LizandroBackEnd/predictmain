import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import type { Severity } from "@/modules/telemetry-ingestion/domain/telemetry-row";

export interface QueueItemView {
  productId: string;
  udi: number;
  type: string;
  severity: Severity;
  airTemp: number;
  rpm: number;
  torque: number;
}

const SEVERITY_LABELS: Record<Severity, string> = {
  critical: "crítica",
  warning: "advertencia",
  ok: "normal",
};

export function OperationsQueue({
  items,
}: {
  items: QueueItemView[];
}): React.JSX.Element {
  if (items.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-[var(--line)] px-4 py-10 text-center text-sm text-[var(--fg-2)]">
        No hay elementos que coincidan con este filtro.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-md border border-[var(--line)]">
      <table className="w-full text-left text-sm">
        <thead className="bg-[var(--raised)] text-[var(--fg-2)]">
          <tr>
            <th className="px-3 py-2 font-medium">Product ID</th>
            <th className="px-3 py-2 font-medium">UDI</th>
            <th className="px-3 py-2 font-medium">Tipo</th>
            <th className="px-3 py-2 font-medium">Severidad</th>
            <th className="px-3 py-2 font-medium">Aire [K]</th>
            <th className="px-3 py-2 font-medium">RPM</th>
            <th className="px-3 py-2 font-medium">Torque</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={`${item.productId}-${item.udi}`}
              className="border-t border-[var(--line)]"
            >
              <td className="px-3 py-2">
                <Link
                  className="font-medium text-[var(--risk)] hover:underline"
                  href={`/assets/${encodeURIComponent(item.productId)}`}
                >
                  {item.productId}
                </Link>
              </td>
              <td className="px-3 py-2 font-mono text-xs">{item.udi}</td>
              <td className="px-3 py-2">{item.type}</td>
              <td className="px-3 py-2">
                <Badge
                  variant={
                    item.severity === "critical"
                      ? "critical"
                      : item.severity === "warning"
                        ? "warning"
                        : "ok"
                  }
                >
                  {SEVERITY_LABELS[item.severity]}
                </Badge>
              </td>
              <td className="px-3 py-2 font-mono text-xs">{item.airTemp}</td>
              <td className="px-3 py-2 font-mono text-xs">{item.rpm}</td>
              <td className="px-3 py-2 font-mono text-xs">{item.torque}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
