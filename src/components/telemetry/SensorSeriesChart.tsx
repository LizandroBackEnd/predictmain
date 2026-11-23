"use client";

import type { JSX } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts";

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

export interface SensorSeriesPoint {
  udi: number;
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
}

const chartConfig = {
  airTemp: { label: "Temp. aire [K]", color: "var(--air)" },
  processTemp: { label: "Temp. proceso [K]", color: "var(--proc)" },
  rpm: { label: "RPM", color: "var(--rpm)" },
  torque: { label: "Torque [Nm]", color: "var(--torque)" },
  toolWear: { label: "Desgaste herramienta [min]", color: "var(--wear)" },
} satisfies ChartConfig;

export function SensorSeriesChart({
  data,
}: {
  data: SensorSeriesPoint[];
}): JSX.Element {
  return (
    <ChartContainer config={chartConfig} className="aspect-[21/9] w-full">
      <LineChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
        <CartesianGrid stroke="var(--grid)" strokeDasharray="3 3" />
        <XAxis
          dataKey="udi"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          label={{ value: "UDI", position: "insideBottomRight", offset: -4 }}
        />
        <YAxis tickLine={false} axisLine={false} width={42} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Legend />
        <Line
          type="monotone"
          dataKey="airTemp"
          stroke="var(--air)"
          dot={false}
          strokeWidth={1.6}
        />
        <Line
          type="monotone"
          dataKey="processTemp"
          stroke="var(--proc)"
          dot={false}
          strokeWidth={1.6}
        />
        <Line
          type="monotone"
          dataKey="rpm"
          stroke="var(--rpm)"
          dot={false}
          strokeWidth={1.6}
        />
        <Line
          type="monotone"
          dataKey="torque"
          stroke="var(--torque)"
          dot={false}
          strokeWidth={1.6}
        />
        <Line
          type="monotone"
          dataKey="toolWear"
          stroke="var(--wear)"
          dot={false}
          strokeWidth={1.6}
        />
      </LineChart>
    </ChartContainer>
  );
}
