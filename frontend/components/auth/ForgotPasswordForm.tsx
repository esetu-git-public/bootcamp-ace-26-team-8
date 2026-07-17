"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/lib/validators";
import { authService } from "@/services/authService";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

export function ForgotPasswordForm() {
  const [formError, setFormError] = useState<string | null>(null);
  const [isSent, setIsSent] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({ resolver: zodResolver(forgotPasswordSchema) });

  const onSubmit = async (values: ForgotPasswordFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await authService.sendPasswordResetEmail(values.email);
      setIsSent(true);
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Couldn't send the reset link. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSent) {
    return (
      <Alert tone="success" title="Reset link sent">
        If an account exists for that email, a password reset link is on its way. It expires
        after 1 hour.
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
      {formError && <Alert tone="danger">{formError}</Alert>}

      <Input
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="you@example.com"
        required
        error={errors.email?.message}
        {...register("email")}
      />

      <Button type="submit" size="lg" isLoading={isSubmitting} className="w-full mt-2">
        Send reset link
      </Button>
    </form>
  );
}