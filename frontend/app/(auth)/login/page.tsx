import type { Metadata } from "next";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { LoginForm } from "@/components/auth/LoginForm";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage() {
  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to check your application status or review the queue."
      footerPrompt="Don't have an account?"
      footerLinkLabel="Create one"
      footerLinkHref={ROUTES.register}
    >
      <LoginForm />
    </AuthLayout>
  );
}