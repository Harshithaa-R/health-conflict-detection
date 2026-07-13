
"use client";

import { useState, useEffect } from "react";
import { DataConflict } from "@/lib/types";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
// import { 
  //aiSummarizedConflictImpactAssessment 
//} from "@/ai/flows/ai-summarized-conflict-impact-assessment";
//import { 
  //aiGeneratedConflictResolutionAssistant 
//} from "@/ai/flows/ai-generated-conflict-resolution-assistant";
import { 
  Loader2, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  ShieldAlert,
  History,
  Info
} from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { Separator } from "@/components/ui/separator";

interface ConflictDetailModalProps {
  conflict: DataConflict | null;
  isOpen: boolean;
  onClose: () => void;
  onResolve: () => void;
}

export function ConflictDetailModal({ conflict, isOpen, onClose, onResolve }: ConflictDetailModalProps) {
  const [loading, setLoading] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [aiData, setAiData] = useState<{
    summary: string;
    explanation: string;
    recommendation: string;
    reliability: string;
  } | null>(null);


  useEffect(() => {
    if (isOpen && conflict) {
      loadAiInsights();
    } else {
      setAiData(null);
    }
  }, [isOpen, conflict]);

  const loadAiInsights = async () => {
  if (!conflict) return;

  setLoading(true);

  try {
    setAiData({
      summary:
        "Conflicting patient information was detected across multiple healthcare sources. Manual review is recommended before finalizing the record.",
      explanation:
        "AI analysis is temporarily disabled. This placeholder keeps the dashboard UI fully functional.",
      recommendation:
        `Use the most reliable source value for "${conflict.field}" and verify with field staff if required.`,
      reliability:
        "Reliability assessment unavailable while AI services are disabled.",
    });
  } catch (error) {
    console.error("AI Insight error:", error);

    toast({
      title: "AI Analysis Failed",
      description: "Could not generate recommendations at this time.",
      variant: "destructive",
    });
  } finally {
    setLoading(false);
  }
};

const handleResolutionAction = (
  decision:
    | "AI Accepted"
    | "Supervisor Manual Override"
    | "Supervisor Rejected AI"
) => {
  toast({
    title: "Conflict Resolved",
    description: `Action: ${decision}`,
  });

  onResolve();
};

  if (!conflict) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/10">
              {conflict.conflictType}
            </Badge>
            <Badge variant="outline" className="text-destructive border-destructive/20 font-bold uppercase">
              {conflict.severity}
            </Badge>
          </div>
          <DialogTitle className="text-2xl font-headline font-bold">
            Data Conflict: {conflict.field}
          </DialogTitle>
          <DialogDescription className="text-base">
            Inconsistency detected for {conflict.patient.name} ({conflict.patientId}) in {conflict.patient.district} district.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 my-4">
          <div className="grid md:grid-cols-2 gap-4">
            {conflict.sourceValues.map((src) => (
              <div key={src.sourceId} className="p-4 rounded-xl border-2 border-muted bg-muted/20 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-2 opacity-10">
                  <History size={40} />
                </div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{src.sourceName}</span>
                  <Badge variant="secondary" className="text-[10px]">Reliability: {(src.reliability * 100).toFixed(0)}%</Badge>
                </div>
                <div className="text-xl font-bold text-primary">
                  {src.value || <span className="text-muted-foreground font-normal italic">None Reported</span>}
                </div>
              </div>
            ))}
          </div>

          <Separator />

          <div className="space-y-4">
            <h4 className="flex items-center gap-2 font-headline font-bold text-lg text-primary">
              <Sparkles size={20} className="text-secondary" />
              AI Impact Assessment & Suggestion
            </h4>
            
            {loading ? (
              <div className="flex flex-col items-center justify-center py-12 space-y-4">
                <Loader2 className="animate-spin text-secondary" size={40} />
                <p className="text-sm font-medium text-muted-foreground">Analyzing sources and cross-referencing records...</p>
              </div>
            ) : aiData ? (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="bg-secondary/5 border-l-4 border-l-secondary p-4 rounded-r-xl">
                  <h5 className="text-xs font-bold text-secondary uppercase tracking-widest mb-1">Health Impact Summary</h5>
                  <p className="text-sm leading-relaxed font-medium">{aiData.summary}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-muted-foreground uppercase flex items-center gap-1">
                      <Info size={14} /> Explanation
                    </h5>
                    <p className="text-sm text-muted-foreground italic">{aiData.explanation}</p>
                  </div>
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-muted-foreground uppercase flex items-center gap-1">
                      <ShieldAlert size={14} /> Reliability Assessment
                    </h5>
                    <p className="text-sm text-muted-foreground italic">{aiData.reliability}</p>
                  </div>
                </div>

                <div className="bg-primary text-white p-5 rounded-xl shadow-lg border border-primary-foreground/10">
                  <h5 className="text-xs font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
                    <CheckCircle2 size={16} /> Recommended Resolution
                  </h5>
                  <p className="font-medium text-lg mb-4">{aiData.recommendation}</p>
                  <div className="flex justify-end gap-2">
                    <Button 
                      variant="secondary" 
                      className="font-bold shadow-md h-9"
                      disabled={resolving}
                      onClick={() => handleResolutionAction('AI Accepted')}
                    >
                      {resolving ? <Loader2 className="animate-spin" size={16} /> : "Accept Recommendation"}
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center border-2 border-dashed rounded-xl">
                <p className="text-muted-foreground">No AI analysis available. Load the record to begin.</p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="ghost" onClick={onClose} className="font-bold">Close</Button>
          <div className="flex gap-2">
            <Button variant="outline" className="border-2 font-bold" disabled={resolving} onClick={() => handleResolutionAction('Supervisor Manual Override')}>
              Manual Edit
            </Button>
            <Button variant="destructive" className="font-bold flex gap-2" disabled={resolving} onClick={() => handleResolutionAction('Supervisor Rejected AI')}>
              <XCircle size={18} /> Reject Both
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
