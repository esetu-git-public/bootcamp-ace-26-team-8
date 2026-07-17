"use client";

import { useState } from "react";
import { KeyRound, Mail, UserCircle, LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { authService } from "@/services/authService";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { initials } from "@/lib/utils";

/**
 * No profile-update endpoint exists in the current backend API design
 * (Section 10 covers auth/loan/officer/health only) — this page is
 * read-only account info plus the two Supabase Auth self-service
 * actions (password reset, sign out) until a PATCH /profile route ships.
 */
export default function ProfilePage() {
  const { user, signOut } = useAuth();
  const [resetSent, setResetSent] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleResetPassword = async () => {
    if (!user?.email) return;
    setIsSending(true);
    try {
      await authService.sendPasswordResetEmail(user.email);
      setResetSent(true);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="font-display font-semibold text-2xl text-ink mb-6">Profile</h1>

      <Card>
        <CardContent className="pt-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-subtle text-brand text-xl font-semibold">
            {initials(user?.fullName ?? user?.email ?? "?")}
          </div>
          <div>
            <p className="font-display font-medium text-lg text-ink">{user?.fullName ?? "—"}</p>
            <p className="text-sm text-ink-muted flex items-center gap-1.5 mt-0.5">
              <Mail className="h-3.5 w-3.5" />
              {user?.email}
            </p>
            <p className="text-xs text-ink-faint mt-1 capitalize flex items-center gap-1.5">
              <UserCircle className="h-3.5 w-3.5" />
              {user?.role} account
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-5">
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Manage your password and session.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {resetSent && (
            <Alert tone="success">A password reset link has been sent to {user?.email}.</Alert>
          )}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-ink">Password</p>
              <p className="text-xs text-ink-muted">Send yourself a reset link by email.</p>
            </div>
            <Button variant="outline" size="sm" isLoading={isSending} onClick={handleResetPassword}>
              <KeyRound className="h-4 w-4" />
              Reset password
            </Button>
          </div>
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <div>
              <p className="text-sm font-medium text-ink">Sign out</p>
              <p className="text-xs text-ink-muted">End your session on this device.</p>
            </div>
            <Button variant="danger" size="sm" onClick={() => void signOut()}>
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}