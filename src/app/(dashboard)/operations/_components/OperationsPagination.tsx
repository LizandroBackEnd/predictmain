import Link from "next/link";

const PAGE_SIZE = 15;

export { PAGE_SIZE };

function buildHref(page: number, severity?: string): string {
  const params = new URLSearchParams();
  if (severity && severity !== "all") {
    params.set("severity", severity);
  }
  if (page > 1) {
    params.set("page", String(page));
  }
  const query = params.toString();
  return query ? `/operations?${query}` : "/operations";
}

export function OperationsPagination({
  page,
  totalItems,
  severity,
}: {
  page: number;
  totalItems: number;
  severity?: string;
}): React.JSX.Element | null {
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  if (totalItems <= PAGE_SIZE) {
    return null;
  }

  const current = Math.min(Math.max(page, 1), totalPages);
  const from = (current - 1) * PAGE_SIZE + 1;
  const to = Math.min(current * PAGE_SIZE, totalItems);

  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm">
      <p className="text-[var(--fg-2)]">
        Mostrando {from}–{to} de {totalItems}
      </p>
      <div className="flex items-center gap-2">
        {current > 1 ? (
          <Link
            href={buildHref(current - 1, severity)}
            className="rounded-md border border-[var(--line)] px-3 py-1.5 text-[var(--fg)] hover:bg-[var(--raised)]"
          >
            Anterior
          </Link>
        ) : (
          <span className="rounded-md border border-[var(--line)] px-3 py-1.5 text-[var(--fg-3)] opacity-50">
            Anterior
          </span>
        )}
        <span className="min-w-24 text-center text-[var(--fg-2)]">
          Página {current} de {totalPages}
        </span>
        {current < totalPages ? (
          <Link
            href={buildHref(current + 1, severity)}
            className="rounded-md border border-[var(--line)] px-3 py-1.5 text-[var(--fg)] hover:bg-[var(--raised)]"
          >
            Siguiente
          </Link>
        ) : (
          <span className="rounded-md border border-[var(--line)] px-3 py-1.5 text-[var(--fg-3)] opacity-50">
            Siguiente
          </span>
        )}
      </div>
    </div>
  );
}
