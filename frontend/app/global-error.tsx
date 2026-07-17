"use client";

import { AlertOctagon } from "lucide-react";

/** Catches errors in the root layout itself — must render its own
 * <html>/<body> since it replaces the root layout entirely when it fires. */
export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body>
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "1rem", textAlign: "center", fontFamily: "sans-serif" }}>
          <AlertOctagon size={48} color="#b3261e" />
          <h1 style={{ marginTop: "1.25rem", fontSize: "1.25rem", fontWeight: 600 }}>The application failed to load</h1>
          <p style={{ marginTop: "0.5rem", color: "#5b6472", maxWidth: "24rem" }}>
            {error.message || "A critical error occurred."}
          </p>
          <button
            onClick={reset}
            style={{ marginTop: "1.5rem", padding: "0.625rem 1.25rem", borderRadius: "6px", background: "#1f8a70", color: "white", border: "none", fontSize: "0.875rem", fontWeight: 500, cursor: "pointer" }}
          >
            Reload
          </button>
        </div>
      </body>
    </html>
  );
}