
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  ChartContainer, 
  ChartTooltip, 
  ChartTooltipContent, 
  ChartLegend, 
  ChartLegendContent 
} from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { MOCK_TRENDS } from "@/lib/mock-data";

const chartConfig = {
  Measurement: { label: "Measurement", color: "hsl(var(--chart-1))" },
  Temporal: { label: "Temporal", color: "hsl(var(--chart-2))" },
  'Missing-in-source': { label: "Missing Data", color: "hsl(var(--chart-3))" },
  Identity: { label: "Identity", color: "hsl(var(--chart-4))" },
};

export function ConflictTrendChart() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="font-headline font-bold text-xl">Conflict Trends</CardTitle>
        <p className="text-xs text-muted-foreground font-medium">Monthly volume by classification class</p>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
          <BarChart data={MOCK_TRENDS}>
            <CartesianGrid vertical={false} strokeDasharray="3 3" opacity={0.3} />
            <XAxis 
              dataKey="month" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fontWeight: 500 }}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 12, fontWeight: 500 }}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar dataKey="Measurement" fill="var(--color-Measurement)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Temporal" fill="var(--color-Temporal)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Missing-in-source" fill="var(--color-Missing-in-source)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Identity" fill="var(--color-Identity)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
