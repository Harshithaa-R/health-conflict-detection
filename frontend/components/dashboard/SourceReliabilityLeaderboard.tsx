
"use client";

import { SourceStats } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ShieldCheck, TrendingUp, AlertTriangle } from "lucide-react";

interface SourceReliabilityLeaderboardProps {
  stats: SourceStats[];
}

export function SourceReliabilityLeaderboard({ stats }: SourceReliabilityLeaderboardProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="font-headline font-bold text-xl">Source Reliability</CardTitle>
          <p className="text-xs text-muted-foreground font-medium">Data accuracy rankings by cadre</p>
        </div>
        <ShieldCheck className="text-primary" size={24} />
      </CardHeader>
      <CardContent className="space-y-6">
        {stats.sort((a, b) => b.accuracyRate - a.accuracyRate).map((source, index) => (
          <div key={source.sourceId} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary border border-primary/20">
                  #{index + 1}
                </div>
                <span className="font-semibold text-sm">{source.sourceName}</span>
              </div>
              <span className="text-sm font-bold text-primary">{(source.accuracyRate * 100).toFixed(1)}%</span>
            </div>
            <Progress 
              value={source.accuracyRate * 100} 
              className="h-2 bg-muted"
            />
            <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase font-bold tracking-tighter">
              <span className="flex items-center gap-1">
                <TrendingUp size={10} /> {source.totalRecords.toLocaleString()} Records
              </span>
              <span className="flex items-center gap-1">
                <AlertTriangle size={10} /> {source.resolvedConflicts} Fixed
              </span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
