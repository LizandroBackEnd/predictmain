import {
  IconActivity,
  IconAlertTriangle,
  IconChartLine,
  IconCpu,
} from "@tabler/icons-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { ThemeToggle } from "@/app/(dashboard)/_components/ThemeToggle";

const NAV = [
  { href: "/operations", label: "Operación", icon: IconAlertTriangle },
  { href: "/assets/M14860", label: "Activos", icon: IconCpu },
  { href: "/telemetry", label: "Telemetría", icon: IconChartLine },
  { href: "/predictions", label: "Predicciones", icon: IconActivity },
] as const;

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}): React.JSX.Element {
  return (
    <div className="flex min-h-screen w-full bg-[var(--bg)] text-[var(--fg)]">
      <aside className="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-[var(--line)] bg-[var(--panel)] p-4">
        <div className="mb-8 flex items-center justify-between gap-2">
          <div>
            <div className="text-xs uppercase tracking-[0.16em] text-[var(--fg-3)]">
              PredictMain
            </div>
            <div className="text-sm font-semibold">Consola operativa</div>
          </div>
          <ThemeToggle />
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-[var(--fg-2)] transition-colors hover:bg-[var(--raised)] hover:text-[var(--fg)]"
              >
                <Icon size={18} stroke={1.6} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <p className="text-[11px] leading-relaxed text-[var(--fg-3)]">
          Datos del CSV procesado AI4I + modelo HU-08 vía FastAPI.
        </p>
      </aside>
      <main className="min-w-0 flex-1 p-6">{children}</main>
    </div>
  );
}
