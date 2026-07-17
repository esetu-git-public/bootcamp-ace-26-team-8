"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { supabase } from "@/lib/supabaseClient";
import { ROUTES } from "@/lib/constants";

const resetPasswordSchema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string().min(8, "Confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type ResetPasswordValues = z.infer<typeof resetPasswordSchema>;

/**
 * Landed on via the reset link Supabase emails from
 * authService.sendPasswordResetEmail — Supabase's client SDK exchanges
 * the URL's recovery token for a session automatically before this page
 * mounts, so updateUser() below applies to the correct account.
 */
export default function ResetPasswordPage() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordValues>({ resolver: zodResolver(resetPasswordSchema) });

  const onSubmit = async (values: ResetPasswordValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      const { error } = await supabase.auth.updateUser({ password: values.password });
      if (error) throw error;
      setIsSuccess(true);
      setTimeout(() => router.replace(ROUTES.login), 2000);
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Couldn't update your password. Request a new link and try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Set a new password"
      subtitle="Choose a new password for your account."
      footerPrompt="Changed your mind?"
      footerLinkLabel="Back to log in"
      footerLinkHref={ROUTES.login}
    >
      {isSuccess ? (
        <Alert tone="success" title="Password updated">
          Redirecting you to log in…
        </Alert>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
          {formError && <Alert tone="danger">{formError}</Alert>}
          <PasswordInput
            label="New password"
            autoComplete="new-password"
            required
            error={errors.password?.message}
            {...register("password")}
          />
          <PasswordInput
            label="Confirm new password"
            autoComplete="new-password"
            required
            error={errors.confirmPassword?.message}
            {...register("confirmPassword")}
          />
          <Button type="submit" size="lg" isLoading={isSubmitting} className="w-full mt-2">
            Update password
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}