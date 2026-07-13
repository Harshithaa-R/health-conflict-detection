
"use client";

import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { ConflictTrendChart } from "@/components/dashboard/ConflictTrendChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip 
} from "recharts";
import { MOCK_TRENDS } from "@/lib/mock-data";
import { TrendingUp, Users, Map, Clock } from "lucide-react";

const SEVERITY_DATA = [
  { name: 'Critical', value: 12, color: '#ef4444' },
  { name: 'High', value: 24, color: '#f97316' },
  { name: 'Medium', value: 45, color: '#eab308' },
  { name: 'Low', value: 19, color: '#22c55e' },
];

export default function AnalyticsPage() {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <SidebarInset className="flex flex-col flex-1">
        <header className="h-20 border-b border-border bg-white/50 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
          <h2 className="font-headline font-bold text-2xl text-primary">Analytics Engine</h2>
        </header>

        <main className="flex-1 p-8 space-y-8 max-w-[1400px] mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ConflictTrendChart />
            
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle className="font-headline font-bold">Severity Distribution</CardTitle>
                <p className="text-sm text-muted-foreground">Current workload composition by priority</p>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={SEVERITY_DATA}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {SEVERITY_DATA.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 text-xs font-bold mt-4">
                  {SEVERITY_DATA.map((s) => (
                    <div key={s.name} className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }}></div>
                      <span>{s.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: "Avg Resolution Time", value: "4.2h", icon: Clock, sub: "-12% vs last week" },
              { label: "Patients Scanned", value: "12,401", icon: Users, sub: "Karnataka Region" },
              { label: "District Coverage", value: "28/31", icon: Map, sub: "Rural health units" },
              { label: "Pipeline Efficiency", value: "94.2%", icon: TrendingUp, sub: "Automated merging" }
            ].map((stat, i) => (
              <Card key={i} className="border-border/50 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="p-2 bg-muted rounded-lg text-primary">
                      <stat.icon size={20} />
                    </div>
                    <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded uppercase">Live</span>
                  </div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">{stat.label}</p>
                  <h4 className="text-2xl font-headline font-bold text-primary">{stat.value}</h4>
                  <p className="text-xs text-muted-foreground mt-2">{stat.sub}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      </SidebarInset>
    </div>
  );
}
