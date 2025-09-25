import React from 'react';
import type { LucideIcon } from 'lucide-react';

import { cn } from '../../lib/utils';

const gradientMap: Record<'slate' | 'indigo' | 'emerald' | 'sunset', string> = {
  slate: 'from-slate-900 via-slate-800 to-slate-900',
  indigo: 'from-indigo-900 via-blue-900 to-slate-900',
  emerald: 'from-emerald-900 via-emerald-800 to-slate-900',
  sunset: 'from-rose-900 via-purple-900 to-indigo-900',
};

export interface HeroStat {
  label: string;
  value: string;
  helper?: string;
  icon?: LucideIcon;
}

export interface PageHeroProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  stats?: HeroStat[];
  media?: React.ReactNode;
  gradient?: 'slate' | 'indigo' | 'emerald' | 'sunset';
  className?: string;
}

export function PageHero({
  eyebrow,
  title,
  description,
  actions,
  stats,
  media,
  gradient = 'indigo',
  className,
}: PageHeroProps) {
  const gradientClass = gradientMap[gradient] ?? gradientMap.indigo;

  return (
    <section
      className={cn(
        'relative overflow-hidden rounded-3xl bg-gradient-to-br text-white shadow-xl',
        'px-6 py-8 md:px-10 md:py-12',
        gradientClass,
        className
      )}
    >
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-16 top-8 h-64 w-64 rounded-full bg-white/15 blur-3xl" />
        <div className="absolute -right-20 bottom-0 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/30 to-transparent" />
      </div>

      <div className="relative z-10 flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
        <div className="space-y-5 text-white">
          {eyebrow && (
            <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-1 text-xs font-semibold uppercase tracking-widest">
              {eyebrow}
            </span>
          )}
          <div className="space-y-3">
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">{title}</h1>
            {description && (
              <p className="max-w-2xl text-sm text-white/80 md:text-base">{description}</p>
            )}
          </div>
          {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
        </div>

        {media && (
          <div className="w-full max-w-sm shrink-0 md:text-right">{media}</div>
        )}
      </div>

      {stats && stats.length > 0 && (
        <div className="relative z-10 mt-8 grid grid-cols-2 gap-3 md:mt-10 md:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="rounded-2xl border border-white/15 bg-white/10 p-4 text-sm backdrop-blur"
              >
                <div className="flex items-center justify-between text-xs uppercase tracking-wide text-white/70">
                  <span>{stat.label}</span>
                  {Icon && <Icon className="h-4 w-4 text-white/80" />}
                </div>
                <div className="mt-2 text-2xl font-semibold text-white">{stat.value}</div>
                {stat.helper && <div className="mt-1 text-xs text-white/70">{stat.helper}</div>}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
