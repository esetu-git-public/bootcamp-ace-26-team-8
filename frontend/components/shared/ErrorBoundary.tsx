"use client";

import { Component, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Structured client-side error log; a production build could forward
    // this to an external sink alongside the backend's request_id logs.
    console.error("[ErrorBoundary] Uncaught error:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger-subtle text-danger">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-display font-medium text-lg text-ink">Something went wrong</h2>
            <p className="text-sm text-ink-muted mt-1 max-w-sm">
              An unexpected error interrupted this page. You can try again, or go back and retry
              your last action.
            </p>
          </div>
          <Button onClick={this.handleReset}>Try again</Button>
        </div>
      );
    }
    return this.props.children;
  }
}