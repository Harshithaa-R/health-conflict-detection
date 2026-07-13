
"use client";

import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { SidebarInset } from "@/components/ui/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  History, 
  CheckCircle2, 
  Search, 
  Download,
  Filter,
  User,
  ExternalLink,
  Loader2
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { useMemo } from "react";
import { MOCK_CONFLICTS } from "@/lib/mock-data";
export default function HistoryPage() {

  const supervisor = {
  assignedDistrict: "Bengaluru Urban"
};

const isLoading = false;

const resolutionsData = MOCK_CONFLICTS.map((conflict, index) => ({
  id: conflict.id,
  conflictId: conflict.id,
  resolutionType: "AI Accepted",
  resolvedValue: conflict.field,
  patientDistrict: conflict.patient.district,
  resolvedAt: "2026-05-31T10:00:00",}));

  // In-memory sorting
  const sortedResolutions = useMemo(() => {
    if (!resolutionsData) return null;
    return [...resolutionsData].sort((a, b) => 
      new Date(b.resolvedAt).getTime() - new Date(a.resolvedAt).getTime()
    ).slice(0, 20);
  }, [resolutionsData]);

  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <SidebarInset className="flex flex-col flex-1">
        <header className="h-20 border-b border-border bg-white/50 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <History className="text-primary" size={24} />
            <h2 className="font-headline font-bold text-2xl text-primary">Audit Trail</h2>
          </div>
          <Button className="font-bold h-10 px-6 rounded-xl gap-2 shadow-lg shadow-primary/20">
            <Download size={18} /> Export CSV
          </Button>
        </header>

        <main className="flex-1 p-8 space-y-8 max-w-[1200px] mx-auto w-full">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <Input placeholder="Filter by patient, source, or resolution method..." className="pl-9 h-11 bg-white border-border shadow-sm rounded-xl" />
            </div>
            <Button variant="outline" className="h-11 rounded-xl border-2 font-bold gap-2">
              <Filter size={18} /> Filters
            </Button>
          </div>

          <Card className="border-border/50 shadow-sm overflow-hidden">
            <CardHeader className="bg-muted/30 border-b">
              <CardTitle className="text-lg font-headline font-bold flex items-center gap-2">
                <CheckCircle2 size={18} className="text-secondary" />
                Recently Resolved Conflicts in {supervisor?.assignedDistrict || '...'}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-12 flex justify-center">
                  <Loader2 className="animate-spin text-primary" size={32} />
                </div>
              ) : (
                <div className="divide-y">
                  {sortedResolutions?.map((item) => (
                    <div key={item.id} className="p-6 hover:bg-muted/10 transition-colors flex items-center justify-between group">
                      <div className="flex items-center gap-6">
                        <div className="bg-muted p-3 rounded-xl text-muted-foreground group-hover:bg-primary/5 group-hover:text-primary transition-colors">
                          <User size={20} />
                        </div>
                        <div className="space-y-1">
                          <h4 className="font-bold text-primary flex items-center gap-2">
                            Case {item.conflictId?.substring(0, 8) || 'Unknown'}
                            <Badge variant="outline" className="text-[10px] font-bold uppercase tracking-wider h-5">
                              {item.resolutionType}
                            </Badge>
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Resolved value: <span className="text-primary font-semibold truncate max-w-[200px] inline-block align-bottom">{item.resolvedValue}</span>
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-12 text-right">
                        <div className="hidden md:block">
                          <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">District</p>
                          <p className="text-sm font-bold text-primary">{item.patientDistrict}</p>
                        </div>
                        <div className="hidden sm:block">
                          <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Timestamp</p>
                          <p className="text-sm text-muted-foreground">
                            {item.resolvedAt ? format(new Date(item.resolvedAt), "MMM d, HH:mm") : 'N/A'}
                          </p>
                        </div>
                        <Button variant="ghost" size="icon" className="rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                          <ExternalLink size={18} />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {!isLoading && (!sortedResolutions || sortedResolutions.length === 0) && (
                    <div className="p-12 text-center text-muted-foreground italic">
                      No resolution records found for {supervisor?.assignedDistrict || 'this district'}.
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
          
          <div className="text-center">
            <Button variant="ghost" className="font-bold text-muted-foreground hover:text-primary">
              Load More Records
            </Button>
          </div>
        </main>
      </SidebarInset>
    </div>
  );
}
