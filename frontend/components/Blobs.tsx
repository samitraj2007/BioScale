/**
 * Decorative, blurred Material You "blobs". Purely presentational and hidden
 * from assistive tech. Motion is gated behind `motion-safe`.
 */
export default function Blobs({ variant = "hero" }: { variant?: "hero" | "soft" }) {
  if (variant === "soft") {
    return (
      <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="blob -left-24 top-10 h-72 w-72 bg-primary/10 motion-safe:animate-blob-float" />
        <div className="blob -right-16 bottom-0 h-64 w-64 bg-tertiary/10 motion-safe:animate-pulse-soft" />
      </div>
    );
  }

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="blob -left-28 -top-24 h-80 w-80 bg-primary/25 motion-safe:animate-blob-float" />
      <div
        className="blob right-[-6rem] top-[-3rem] h-96 w-96 bg-tertiary/20 motion-safe:animate-blob-float"
        style={{ animationDelay: "-6s" }}
      />
      <div className="blob bottom-[-8rem] left-1/3 h-80 w-80 bg-secondary-container/50 motion-safe:animate-pulse-soft" />
    </div>
  );
}
