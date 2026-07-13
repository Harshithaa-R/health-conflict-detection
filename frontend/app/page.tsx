
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { ConflictCard } from "@/components/dashboard/ConflictCard";
import { SourceReliabilityLeaderboard } from "@/components/dashboard/SourceReliabilityLeaderboard";
import { ConflictTrendChart } from "@/components/dashboard/ConflictTrendChart";
import { ConflictDetailModal } from "@/components/dashboard/ConflictDetailModal";

import { 
  MOCK_SOURCE_STATS,
  MOCK_CONFLICTS
} from "@/lib/mock-data";
import { 
  Bell, 
  Search, 
  Filter, 
  LayoutGrid, 
  List,
  ChevronRight,
  Plus,
  Sparkles,
  Loader2,
  Database,
  AlertTriangle,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DataConflict } from "@/lib/types";
import { toast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function Dashboard() {
  const router = useRouter();
  const [selectedConflict, setSelectedConflict] = useState<DataConflict | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSeeding] = useState(false);
  const isConflictsLoading = false;
const isSupervisorLoading = false;
const conflictsError = null;

const supervisor = {
  assignedDistrict: "Bengaluru Urban"
};
  // In-memory sorting to avoid composite index requirement
  const sortedConflicts = MOCK_CONFLICTS;
  const seedSampleData = () => {
  toast({
    title: "Demo Mode",
    description: "Using local mock data. FastAPI integration will be added later."
  });
};
  const handleViewDetails = (id: string) => {
  const conflict = sortedConflicts.find(
    (c) => c.id === id
  );

  if (conflict) {
    setSelectedConflict(conflict);
    setIsModalOpen(true);
  }
};

  return (
    <div className="flex min-h-screen w-full bg-background transition-colors duration-300">
      <AppSidebar />
      <SidebarInset className="flex flex-col flex-1">
        <header className="h-20 border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
          <div className="flex items-center gap-8 flex-1">
            <h2 className="font-headline font-bold text-2xl text-primary hidden md:block">Supervisor Dashboard</h2>
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input 
                placeholder="Search patient, ID, or district..." 
                className="pl-10 h-11 bg-muted/50 border-transparent focus:bg-background focus:border-primary transition-all rounded-xl"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" className="h-11 w-11 rounded-xl relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-destructive border-2 border-white rounded-full"></span>
            </Button>
            <Button 
              className="font-bold h-11 px-6 rounded-xl hidden sm:flex gap-2 shadow-lg shadow-primary/20"
              onClick={seedSampleData}
              disabled={isSeeding}
            >
              {isSeeding ? <Loader2 className="animate-spin" size={18} /> : <Plus size={18} />}
              Sync Sample Data
            </Button>
          </div>
        </header>

        <main className="flex-1 p-8 space-y-8 max-w-[1600px] mx-auto w-full">
          {conflictsError && (
            <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle className="font-bold">Database Error</AlertTitle>
              <AlertDescription className="text-sm">
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: "Active Conflicts", value: sortedConflicts?.length || 0, sub: `In ${supervisor?.assignedDistrict || '...'}`, trend: "up", color: "text-destructive" },
              { label: "Resolved Today", value: 14, sub: "Across 4 cadres", trend: "up", color: "text-secondary" },
              { label: "Avg. Reliability", value: "88.4%", sub: "Source composite", trend: "stable", color: "text-primary" },
              { label: "Sync Latency", value: "1.2s", sub: "Pipeline health", trend: "down", color: "text-emerald-600" }
            ].map((stat, i) => (
              <div key={i} className="p-6 bg-card rounded-2xl border border-border/50 shadow-sm space-y-2">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{stat.label}</p>
                <div className="flex items-baseline gap-2">
                  <h4 className={`text-3xl font-headline font-bold ${stat.color}`}>{stat.value}</h4>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{stat.trend}</span>
                </div>
                <p className="text-xs text-muted-foreground">{stat.sub}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <section className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-headline font-bold text-2xl flex items-center gap-2">
                    Priority Conflict Queue
                    <span className="text-sm font-normal bg-muted px-3 py-1 rounded-full text-muted-foreground">{sortedConflicts?.length || 0} cases</span>
                  </h3>
                  <p className="text-sm text-muted-foreground">AI-filtered conflicts for {supervisor?.assignedDistrict || 'your region'}.</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg bg-card border">
                    <LayoutGrid size={18} />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg">
                    <List size={18} />
                  </Button>
                  <Button variant="outline" className="gap-2 border-2 font-bold h-9">
                    <Filter size={16} /> Filters
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {(isConflictsLoading || isSupervisorLoading || isSeeding) ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="h-64 bg-muted animate-pulse rounded-2xl" />
                  ))
                ) : sortedConflicts?.map((conflict) => (
                  <ConflictCard 
                    key={conflict.id} 
                    conflict={conflict} 
                    onViewDetails={handleViewDetails}
                  />
                ))}
                {!isConflictsLoading && !isSupervisorLoading && !isSeeding && (!sortedConflicts || sortedConflicts.length === 0) && (
                  <div className="col-span-2 py-20 text-center bg-card rounded-3xl border-2 border-dashed flex flex-col items-center justify-center space-y-4">
                    <div className="p-4 bg-emerald-50 text-emerald-600 rounded-full">
                      <Database size={32} />
                    </div>
                    <div>
                      <h4 className="font-headline font-bold text-xl">Queue Empty</h4>
                      <p className="text-muted-foreground">No pending data conflicts in {supervisor?.assignedDistrict}.</p>
                      <p className="text-xs text-muted-foreground mt-1 italic">Click "Sync Sample Data" above to populate your regional queue.</p>
                    </div>
                    <Button 
                      variant="outline" 
                      className="font-bold border-2"
                      onClick={seedSampleData}
                      disabled={isSeeding}
                    >
                      {isSeeding ? "Syncing..." : "Sync Sample Data"}
                    </Button>
                  </div>
                )}
              </div>
              
              {sortedConflicts && sortedConflicts.length > 0 && (
                <div className="flex justify-center">
                  <Button variant="ghost" className="gap-2 font-bold group" onClick={() => router.push('/conflicts')}>
                    View Complete Queue <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </Button>
                </div>
              )}
            </section>

            <aside className="space-y-8">
              <SourceReliabilityLeaderboard stats={MOCK_SOURCE_STATS} />
              <ConflictTrendChart />
              
              <div className="p-6 bg-primary rounded-2xl text-primary-foreground relative overflow-hidden shadow-xl shadow-primary/20">
                <div className="absolute -bottom-10 -right-10 opacity-10">
                  <Sparkles size={180} />
                </div>
                <h4 className="font-headline font-bold text-lg mb-2 relative z-10">AI Pipeline Performance</h4>
                <p className="opacity-80 text-sm relative z-10 mb-6">
                  The XGBoost classifier currently has an F1 score of 0.94 on Karnataka synthetic test sets.
                </p>
                <div className="space-y-4 relative z-10">
                  <div className="flex justify-between text-xs font-bold uppercase tracking-widest">
                    <span>Auto-Resolved</span>
                    <span>82%</span>
                  </div>
                  <div className="h-2 bg-white/20 rounded-full">
                    <div className="h-full bg-secondary w-[82%] rounded-full shadow-[0_0_10px_rgba(38,172,218,0.5)]"></div>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </main>
      </SidebarInset>

      <ConflictDetailModal 
        conflict={selectedConflict}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onResolve={() => setIsModalOpen(false)}
      />
    </div>
  );
}
