'use client';

import { useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import type { LucideIcon } from 'lucide-react';
import { Home, Dumbbell, Sparkles, User, Package } from 'lucide-react';

import { cn } from '../../lib/utils';

export type MobileNavKey = 'home' | 'generate' | 'equipment' | 'programs' | 'profile';

interface BottomNavItem {
  key: MobileNavKey;
  label: string;
  href: string;
  icon: LucideIcon;
}

interface MobileBottomNavProps {
  current?: MobileNavKey;
  className?: string;
}

const NAV_ITEMS: BottomNavItem[] = [
  { key: 'home', label: 'Home', href: '/', icon: Home },
  { key: 'generate', label: 'Generate', href: '/generate', icon: Sparkles },
  { key: 'equipment', label: 'Equipment', href: '/equipment', icon: Package },
  { key: 'programs', label: 'Programs', href: '/workouts/saved', icon: Dumbbell },
  { key: 'profile', label: 'Profile', href: '/profile', icon: User },
];

export function MobileBottomNav({ current, className }: MobileBottomNavProps) {
  const pathname = usePathname();
  const router = useRouter();

  const activeKey = useMemo<MobileNavKey>(() => {
    if (current) return current;

    const match = NAV_ITEMS.find((item) => pathname?.startsWith(item.href));
    return match?.key ?? 'home';
  }, [current, pathname]);

  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 z-50 border-t border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60',
        'md:hidden',
        className
      )}
    >
      <div className="mx-auto flex max-w-md items-center justify-around px-3 py-3 text-xs font-medium">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeKey === item.key;

          return (
            <button
              key={item.key}
              type="button"
              onClick={() => router.push(item.href)}
              className={cn(
                'flex flex-col items-center gap-1 rounded-full px-2 py-2 transition-colors',
                isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className={cn('h-5 w-5', isActive && 'drop-shadow-sm')} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
