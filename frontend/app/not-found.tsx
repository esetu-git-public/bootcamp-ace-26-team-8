import Link from "next/link";
import { FileQuestion } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ROUTES } from "@/lib/constants";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-surface-inset text-ink-faint mb-5">
        <FileQuestion className="h-7 w-7" />
      </div>
      <p className="figure text-5xl font-semibold text-ink">404</p>
      <h1 className="font-display font-medium text-xl text-ink mt-3">Page not found</h1>
      <p className="text-sm text-ink-muted mt-2 max-w-sm">
        The page you're looking for doesn't exist, or you may not have access to it.
      </p>
      <Link href={ROUTES.home} className="mt-6">
        <Button>Back to home</Button>
      </Link>
    </div>
  );
}