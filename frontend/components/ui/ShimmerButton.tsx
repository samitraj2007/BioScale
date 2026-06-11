import Link from "next/link";
import { type ReactNode } from "react";

interface ShimmerButtonProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  icon?: ReactNode;
  href?: string;
}

const buttonClass =
  "group relative inline-flex overflow-hidden rounded-full bg-[#4A1D96] px-8 py-3 text-base font-semibold text-purple-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#6750A4] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

function SweepContent({
  children,
  icon,
}: {
  children: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <>
      <span
        aria-hidden
        className="absolute bottom-0 left-0 h-48 w-full origin-bottom translate-y-full rounded-full bg-white/15 transition-transform duration-300 ease-out group-hover:translate-y-10"
      />
      <span className="relative inline-flex items-center justify-center gap-2">
        {children}
        {icon}
      </span>
    </>
  );
}

export default function ShimmerButton({
  children,
  className,
  onClick,
  type = "button",
  disabled = false,
  icon,
  href,
}: ShimmerButtonProps) {
  const classes = [buttonClass, className].filter(Boolean).join(" ");

  if (href) {
    return (
      <Link href={href} className={classes}>
        <SweepContent icon={icon}>{children}</SweepContent>
      </Link>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={classes}
    >
      <SweepContent icon={icon}>{children}</SweepContent>
    </button>
  );
}
