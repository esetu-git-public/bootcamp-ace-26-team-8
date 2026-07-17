import { CustomerSidebarShell } from "@/components/customer/CustomerSidebarShell";

export default function CustomerLayout({ children }: { children: React.ReactNode }) {
  return <CustomerSidebarShell>{children}</CustomerSidebarShell>;
}