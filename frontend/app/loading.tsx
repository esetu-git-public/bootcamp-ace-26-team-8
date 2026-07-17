import { FullPageSpinner } from "@/components/ui/Spinner";

/** Next.js App Router special file — shown automatically during any
 * route segment's server data fetch/navigation, site-wide fallback. */
export default function RootLoading() {
  return <FullPageSpinner label="Loading…" />;
}