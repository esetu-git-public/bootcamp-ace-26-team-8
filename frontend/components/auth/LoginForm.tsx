"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { loginSchema, type LoginFormValues } from "@/lib/validators";
import { useAuth } from "@/hooks/useAuth";
import { authService } from "@/services/authService";
import { Input } from "@/components/ui/Input";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { ROUTES } from "@/lib/constants";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signIn } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (values: LoginFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await signIn(values.email, values.password);
      const session = await authService.verifySession();
      const redirectTo = searchParams.get("redirectTo");
      const destination =
        redirectTo ?? (session.role === "officer" ? ROUTES.officerDashboard : ROUTES.customerDashboard);
      router.replace(destination);
      router.refresh();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Couldn't sign you in. Check your email and password."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

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

      <div>
        <PasswordInput
          label="Password"
          autoComplete="current-password"
          placeholder="••••••••"
          required
          error={errors.password?.message}
          {...register("password")}
        />
        <div className="flex justify-end mt-1.5">
          <Link href={ROUTES.forgotPassword} className="text-xs text-brand hover:text-brand-hover font-medium">
            Forgot password?
          </Link>
        </div>
      </div>

      <Button type="submit" size="lg" isLoading={isSubmitting} className="w-full mt-2">
        Log in
      </Button>
    </form>
  );
}