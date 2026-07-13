
"use client";

import { useState, useMemo } from "react";
import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { ConflictCard } from "@/components/dashboard/ConflictCard";
import { ConflictDetailModal } from "@/components/dashboard/ConflictDetailModal";
import { MOCK_CONFLICTS } from "@/lib/mock-data";
import { 
  Search, 
  Filter, 
  AlertCircle,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DataConflict } from "@/lib/types";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function ConflictsPage() {
  const [selectedConflict, setSelectedConflict] = useState<DataConflict | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("all");
    
  // In-memory sorting
  const supervisor = {
  assignedDistrict: "Bengaluru Urban"
};

const isLoading = false;
const conflictsError = null;

const sortedConflicts = useMemo(() => {
  if (activeTab === "all") return MOCK_CONFLICTS;

  return MOCK_CONFLICTS.filter(
    (c) => c.severity.toLowerCase() === activeTab.toLowerCase()
  );
}, [activeTab]);

  const handleViewDetails = (id: string) => {
  const conflict = sortedConflicts.find(c => c.id === id);
    if (conflict) {
      setSelectedConflict(conflict);
      setIsModalOpen(true);
    }
  };

  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <SidebarInset className="flex flex-col flex-1">
        <header className="h-20 border-b border-border bg-white/50 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="font-headline font-bold text-2xl text-primary">Conflict Queue</h2>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative w-64 hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <Input placeholder="Search records..." className="pl-9 h-10 rounded-xl bg-muted/50 border-transparent focus:bg-white" />
            </div>
            <Button variant="outline" className="rounded-xl border-2 font-bold h-10 gap-2">
              <Filter size={16} /> Filter
            </Button>
          </div>
        </header>

        <main className="flex-1 p-8 space-y-8 max-w-[1200px] mx-auto w-full">
          {conflictsError && (
            <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive mb-6">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle className="font-bold">Database Error</AlertTitle>
              <AlertDescription className="text-sm">
                {conflictsError.message}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <Tabs defaultValue="all" className="w-full sm:w-auto" onValueChange={setActiveTab}>
              <TabsList className="bg-muted/50 p-1 rounded-xl">
                <TabsTrigger value="all" className="rounded-lg px-6 font-bold">All</TabsTrigger>
                <TabsTrigger value="critical" className="rounded-lg px-6 font-bold text-destructive">Critical</TabsTrigger>
                <TabsTrigger value="high" className="rounded-lg px-6 font-bold text-orange-600">High</TabsTrigger>
                <TabsTrigger value="medium" className="rounded-lg px-6 font-bold text-yellow-600">Medium</TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <AlertCircle size={16} className="text-destructive" />
                <span className="font-bold">{sortedConflicts?.length || 0} Pending</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-secondary" />
                <span className="font-bold">{supervisor?.assignedDistrict || 'Loading...'}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {isLoading ? (
               Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-64 bg-muted animate-pulse rounded-2xl" />
              ))
            ) : sortedConflicts?.map((conflict) => (
                <ConflictCard 
                  key={conflict.id} 
                  conflict={conflict} 
                  onViewDetails={handleViewDetails}
                />
              ))}
            
            {!isLoading && (!sortedConflicts || sortedConflicts.length === 0) && !conflictsError && (
              <div className="col-span-full py-32 text-center bg-white rounded-3xl border-2 border-dashed flex flex-col items-center justify-center space-y-4">
                <div className="p-4 bg-muted rounded-full">
                  <CheckCircle2 size={40} className="text-muted-foreground" />
                </div>
                <h3 className="font-headline font-bold text-xl">No Pending Conflicts</h3>
                <p className="text-muted-foreground">The queue for {supervisor?.assignedDistrict} is currently empty.</p>
              </div>
            )}
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
