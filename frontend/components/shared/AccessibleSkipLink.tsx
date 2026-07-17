/** Standard skip-to-content link — invisible until keyboard-focused,
 * lets keyboard/screen-reader users bypass the nav on every page.
 */
export function AccessibleSkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:bg-navy focus:text-white focus:px-4 focus:py-2 focus:rounded focus:text-sm focus:font-medium"
    >
      Skip to main content
    </a>
  );
}