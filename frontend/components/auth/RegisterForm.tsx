"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema, type RegisterFormValues } from "@/lib/validators";
import { useAuth } from "@/hooks/useAuth";
import { authService } from "@/services/authService";
import { Input } from "@/components/ui/Input";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { ROUTES } from "@/lib/constants";

export function RegisterForm() {
  const router = useRouter();
  const { signUp } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const [confirmationSent, setConfirmationSent] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "customer" },
  });

  const onSubmit = async (values: RegisterFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await signUp(values.email, values.password, values.fullName, values.role);
      try {
        const session = await authService.verifySession();
        router.replace(session.role === "officer" ? ROUTES.officerDashboard : ROUTES.customerDashboard);
        router.refresh();
        return;
      } catch {
        // No active session yet — email confirmation is required.
        setConfirmationSent(true);
      }
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Couldn't create your account. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (confirmationSent) {
    return (
      <Alert tone="success" title="Check your email">
        We've sent a confirmation link to your inbox. Confirm your address, then log in to
        continue.
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
      {formError && <Alert tone="danger">{formError}</Alert>}

      <Input
        label="Full name"
        autoComplete="name"
        placeholder="Jordan Rivera"
        required
        error={errors.fullName?.message}
        {...register("fullName")}
      />

      <Input
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="you@example.com"
        required
        error={errors.email?.message}
        {...register("email")}
      />

      <Select
        label="I am a…"
        required
        error={errors.role?.message}
        options={[
          { label: "Customer applying for a loan", value: "customer" },
          { label: "Loan officer", value: "officer" },
        ]}
        {...register("role")}
      />

      <PasswordInput
        label="Password"
        autoComplete="new-password"
        placeholder="At least 8 characters"
        required
        error={errors.password?.message}
        {...register("password")}
      />

      <PasswordInput
        label="Confirm password"
        autoComplete="new-password"
        placeholder="Re-enter your password"
        required
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      <Button type="submit" size="lg" isLoading={isSubmitting} className="w-full mt-2">
        Create account
      </Button>
    </form>
  );
}