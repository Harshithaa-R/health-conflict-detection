
"use client";

import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { MOCK_SOURCE_STATS } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { 
  ShieldCheck, 
  BarChart3, 
  Clock, 
  FileText, 
  AlertTriangle,
  ArrowUpRight,
  Activity
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function SourcesPage() {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <SidebarInset className="flex flex-col flex-1">
        <header className="h-20 border-b border-border bg-white/50 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
          <h2 className="font-headline font-bold text-2xl text-primary">Source Reliability</h2>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-bold border-2 gap-1 px-3 py-1">
              <Activity size={14} /> System Online
            </Badge>
          </div>
        </header>

        <main className="flex-1 p-8 space-y-8 max-w-[1400px] mx-auto w-full">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-primary text-white border-none shadow-xl shadow-primary/20">
              <CardContent className="p-6 space-y-2">
                <p className="text-xs font-bold uppercase tracking-widest opacity-80">Composite Accuracy</p>
                <h3 className="text-4xl font-headline font-bold">88.4%</h3>
                <p className="text-sm opacity-80">+1.2% from last month</p>
              </CardContent>
            </Card>
            {[
              { label: "Active Sources", value: "4", icon: ShieldCheck },
              { label: "Total Records", value: "42.9k", icon: FileText },
              { label: "Validation Errors", value: "1.2%", icon: AlertTriangle }
            ].map((stat, i) => (
              <Card key={i} className="border-border/50 shadow-sm">
                <CardContent className="p-6 flex items-center gap-4">
                  <div className="p-3 bg-muted rounded-xl text-primary">
                    <stat.icon size={24} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{stat.label}</p>
                    <h4 className="text-2xl font-headline font-bold text-primary">{stat.value}</h4>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-8">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle className="font-headline font-bold">Cadre Performance Rankings</CardTitle>
                <p className="text-sm text-muted-foreground">Detailed reliability metrics for field data collection sources.</p>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-muted/30 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        <th className="px-6 py-4 text-left">Source Name</th>
                        <th className="px-6 py-4 text-center">Accuracy Rate</th>
                        <th className="px-6 py-4 text-center">Resolved Conflicts</th>
                        <th className="px-6 py-4 text-center">Total Syncs</th>
                        <th className="px-6 py-4 text-right">Last Audit</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {MOCK_SOURCE_STATS.map((source) => (
                        <tr key={source.sourceId} className="hover:bg-muted/20 transition-colors">
                          <td className="px-6 py-5">
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-primary/5 text-primary rounded-lg">
                                <ShieldCheck size={18} />
                              </div>
                              <span className="font-bold text-primary">{source.sourceName}</span>
                            </div>
                          </td>
                          <td className="px-6 py-5">
                            <div className="flex flex-col items-center gap-1">
                              <span className="text-sm font-bold text-primary">{(source.accuracyRate * 100).toFixed(1)}%</span>
                              <Progress value={source.accuracyRate * 100} className="h-1.5 w-24" />
                            </div>
                          </td>
                          <td className="px-6 py-5 text-center font-medium text-muted-foreground">
                            {source.resolvedConflicts}
                          </td>
                          <td className="px-6 py-5 text-center font-medium text-muted-foreground">
                            {source.totalRecords.toLocaleString()}
                          </td>
                          <td className="px-6 py-5 text-right font-medium text-muted-foreground">
                            {source.lastUpdated}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </SidebarInset>
    </div>
  );
}
