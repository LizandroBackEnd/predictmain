import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "border-[var(--line)] bg-[var(--raised)] text-[var(--fg)]",
        critical:
          "border-transparent bg-[var(--crit-fill)] text-[var(--crit)]",
        warning:
          "border-transparent bg-[var(--warn-fill)] text-[var(--warn)]",
        ok: "border-transparent bg-[color-mix(in_oklab,var(--ok)_18%,transparent)] text-[var(--ok)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({
  className,
  variant,
  ...props
}: BadgeProps): React.JSX.Element {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
