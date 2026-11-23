"use client";

import { IconMoon, IconSun } from "@tabler/icons-react";
import { useTheme } from "next-themes";
import type { JSX } from "react";

import { Button } from "@/components/ui/button";

export function ThemeToggle(): JSX.Element {
  const { resolvedTheme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Cambiar tema"
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
    >
      <IconSun size={18} className="hidden dark:block" />
      <IconMoon size={18} className="block dark:hidden" />
    </Button>
  );
}
