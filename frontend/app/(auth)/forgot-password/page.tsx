import type { Metadata } from "next";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";
import { ROUTES } from "@/lib/constants";

export const metadata: Metadata = { title: "Reset your password" };

export default function ForgotPasswordPage() {
  return (
    <AuthLayout
      title="Reset your password"
      subtitle="Enter your email and we'll send you a link to set a new one."
      footerPrompt="Remembered it after all?"
      footerLinkLabel="Log in"
      footerLinkHref={ROUTES.login}
    >
      <ForgotPasswordForm />
    </AuthLayout>
  );
}