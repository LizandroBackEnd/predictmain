import { IconArrowLeft } from "@tabler/icons-react";
import Link from "next/link";

export function BackLink({
  href,
  label = "Regresar",
}: {
  href: string;
  label?: string;
}): React.JSX.Element {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1.5 text-sm text-[var(--fg-2)] transition-colors hover:text-[var(--fg)]"
    >
      <IconArrowLeft size={16} stroke={1.8} aria-hidden />
      {label}
    </Link>
  );
}
