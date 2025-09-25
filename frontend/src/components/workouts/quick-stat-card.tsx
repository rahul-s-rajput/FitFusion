import React from 'react';
import type { LucideIcon } from 'lucide-react';

import { cn } from '../../lib/utils';

interface QuickStatCardProps {
  title: string;
  value: string;
  helper?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
  };
  className?: string;
}

const trendColors: Record<'up' | 'down' | 'neutral', string> = {
  up: 'text-emerald-600',
  down: 'text-rose-600',
  neutral: 'text-muted-foreground',
};

export function QuickStatCard({ title, value, helper, icon: Icon, trend, className }: QuickStatCardProps) {
  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-2xl border border-border/60 bg-card/80 p-4 shadow-sm transition hover:border-primary/40 hover:shadow-lg',
        className
      )}
    >
      <div className="absolute right-0 top-0 h-16 w-16 -translate-y-8 translate-x-8 rounded-full bg-primary/10 transition group-hover:translate-x-6 group-hover:translate-y-6" />
      <div className="relative z-10 flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{title}</p>
          <div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div>
          {helper && <p className="mt-1 text-xs text-muted-foreground">{helper}</p>}
          {trend && (
            <p className={cn('mt-2 text-xs font-medium', trendColors[trend.direction])}>{trend.value}</p>
          )}
        </div>
        {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
      </div>
    </div>
  );
}
