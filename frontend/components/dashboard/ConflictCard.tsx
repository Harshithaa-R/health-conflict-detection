
"use client";

import { DataConflict } from "@/lib/types";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, MapPin, User, ArrowRight, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

interface ConflictCardProps {
  conflict: DataConflict;
  onViewDetails: (id: string) => void;
}

export function ConflictCard({ conflict, onViewDetails }: ConflictCardProps) {
  const severityColor = {
    low: "bg-blue-100 text-blue-700 border-blue-200",
    medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
    high: "bg-orange-100 text-orange-700 border-orange-200",
    critical: "bg-destructive/10 text-destructive border-destructive/20",
  };

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 border-l-4 border-l-primary group">
      <CardHeader className="p-5 pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{conflict.id}</span>
              <Badge variant="outline" className={cn("text-[10px] uppercase font-bold", severityColor[conflict.severity])}>
                {conflict.severity}
              </Badge>
            </div>
            <h3 className="text-lg font-headline font-bold group-hover:text-primary transition-colors">
              {conflict.patient.name}
            </h3>
          </div>
          <div className="bg-muted p-2 rounded-lg text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">
            <User size={18} />
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-5 pt-2 space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MapPin size={14} className="shrink-0" />
            <span className="truncate">{conflict.patient.district}</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock size={14} className="shrink-0" />
            <span>{formatDistanceToNow(new Date(conflict.detectedAt))} ago</span>
          </div>
        </div>

        <div className="p-3 bg-muted/50 rounded-lg border border-border/50">
          <p className="text-[10px] font-bold text-muted-foreground uppercase mb-1">Conflicting Field</p>
          <div className="flex items-center gap-2">
            <AlertCircle size={14} className="text-secondary" />
            <span className="font-semibold text-primary">{conflict.field}</span>
          </div>
          <p className="text-xs text-muted-foreground mt-2 italic">
            Detected between {conflict.sourceValues.map(s => s.sourceName).join(" & ")}
          </p>
        </div>
      </CardContent>

      <CardFooter className="p-5 pt-0 flex gap-2">
        <Button 
          variant="outline" 
          className="w-full font-bold h-10 border-2"
          onClick={() => onViewDetails(conflict.id)}
        >
          View Details
        </Button>
        <Button 
          className="shrink-0 h-10 w-10 p-0 shadow-lg shadow-primary/20"
          onClick={() => onViewDetails(conflict.id)}
        >
          <ArrowRight size={18} />
        </Button>
      </CardFooter>
    </Card>
  );
}
