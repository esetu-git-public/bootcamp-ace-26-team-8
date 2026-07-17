"use client";

import { Navbar } from "@/components/shared/Navbar";
import { Sidebar } from "@/components/shared/Sidebar";
import { RoleGuard } from "@/components/shared/RoleGuard";

export function CustomerSidebarShell({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allow="customer">
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main id="main-content" className="flex-1 px-4 sm:px-6 lg:px-8 py-8 max-w-6xl mx-auto w-full">{children}</main>
        </div>
      </div>
    </RoleGuard>
  );
}