import { OfficerSidebarShell } from "@/components/officer/OfficerSidebarShell";

export default function OfficerLayout({ children }: { children: React.ReactNode }) {
  return <OfficerSidebarShell>{children}</OfficerSidebarShell>;
}