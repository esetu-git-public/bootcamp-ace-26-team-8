"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { LucideIcon } from "lucide-react";
import { LayoutDashboard, FileText, ClipboardList, UserCircle, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRole } from "@/hooks/useRole";
import { ROUTES } from "@/lib/constants";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const customerItems: NavItem[] = [
  { label: "Dashboard", href: ROUTES.customerDashboard, icon: LayoutDashboard },
  { label: "Apply for a Loan", href: ROUTES.customerApply, icon: FileText },
  { label: "My Applications", href: ROUTES.customerApplications, icon: ClipboardList },
  { label: "Profile", href: ROUTES.customerProfile, icon: UserCircle },
];

const officerItems: NavItem[] = [
  { label: "Dashboard", href: ROUTES.officerDashboard, icon: LayoutDashboard },
  { label: "Applications", href: ROUTES.officerApplications, icon: ClipboardList },
  { label: "Analytics", href: ROUTES.officerAnalytics, icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isOfficer } = useRole();
  const items = isOfficer ? officerItems : customerItems;

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-60 shrink-0 border-r border-border bg-surface min-h-[calc(100vh-4rem)] py-6 px-3">
      <nav className="flex flex-col gap-1">
        {items.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-subtle text-brand"
                  : "text-ink-muted hover:bg-surface-inset hover:text-ink"
              )}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}