"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { contactSchema, type ContactFormValues } from "@/lib/validators";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

/**
 * Contact is a static informational surface — no backend endpoint exists
 * for message delivery in the current API design (Section 10), so this
 * submits to a mailto fallback while presenting a normal in-app form
 * experience. Swap the onSubmit body for a real endpoint if one is added.
 */
export function ContactForm() {
  const [isSent, setIsSent] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ContactFormValues>({ resolver: zodResolver(contactSchema) });

  const onSubmit = async (values: ContactFormValues) => {
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    const subject = encodeURIComponent(`Message from ${values.name}`);
    const body = encodeURIComponent(`${values.message}\n\nReply to: ${values.email}`);
    window.location.href = `mailto:support@ledger.app?subject=${subject}&body=${body}`;
    setIsSubmitting(false);
    setIsSent(true);
    reset();
  };

  if (isSent) {
    return (
      <Alert tone="success" title="Message ready to send">
        Your email client should have opened with your message pre-filled. If it didn't, email us
        directly at support@ledger.app.
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
      <Input label="Name" required error={errors.name?.message} {...register("name")} />
      <Input
        label="Email"
        type="email"
        required
        error={errors.email?.message}
        {...register("email")}
      />
      <Textarea
        label="Message"
        required
        placeholder="How can we help?"
        error={errors.message?.message}
        {...register("message")}
      />
      <Button type="submit" size="lg" isLoading={isSubmitting} className="self-start">
        Send message
      </Button>
    </form>
  );
}