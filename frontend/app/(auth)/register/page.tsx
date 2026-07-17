import type { Metadata } from "next";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Create your account" };

export default function RegisterPage() {
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Apply for a loan or review applications as a loan officer."
      footerPrompt="Already have an account?"
      footerLinkLabel="Log in"
      footerLinkHref={ROUTES.login}
    >
      <RegisterForm />
    </AuthLayout>
  );
}