"use client";

import { Pinyon_Script } from "next/font/google";
import Link from "next/link";
import { usePathname } from "next/navigation";

const pinyonScript = Pinyon_Script({
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

const links = [
  { href: "/", label: "Overview" },
  { href: "/tool", label: "Tool" },
  { href: "/methods", label: "Methods" },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function NavBar() {
  const pathname = usePathname() ?? "/";

  return (
    <header className="sticky top-0 z-40 border-b border-outline-variant/25 bg-[rgba(245,243,235,0.72)] shadow-[0_1px_0_rgba(31,41,51,0.04)] backdrop-blur-[8px]">
      <nav className="container-content flex h-16 items-center justify-between gap-6 sm:gap-8">
        <Link
          href="/"
          className="flex shrink-0 items-center py-1 transition-opacity duration-200 ease-in-out hover:opacity-90"
        >
          <span
            className={`${pinyonScript.className} translate-y-px text-[2.25rem] leading-none tracking-tight text-on-primary-container`}
          >
            Bioscale
          </span>
        </Link>

        <div className="flex items-center gap-3 sm:gap-4">
          <ul className="flex items-center gap-0.5 sm:gap-1">
            {links.map((link) => {
              const active = isActive(pathname, link.href);
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    aria-current={active ? "page" : undefined}
                    className={[
                      "inline-flex items-center border-b-2 px-3 py-2 text-label-lg transition-[color,border-color] duration-200 ease-in-out sm:px-4",
                      active
                        ? "border-primary font-medium text-primary"
                        : "border-transparent text-on-surface-variant hover:border-primary/30 hover:text-primary",
                    ].join(" ")}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>

          <Link
            href="/tool"
            className="ml-1 hidden items-center justify-center rounded-full bg-primary px-5 py-2 text-label-md font-medium text-on-primary shadow-sm transition-all duration-200 ease-in-out hover:bg-[#16603B] hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 motion-safe:active:scale-[0.98] sm:ml-2 sm:inline-flex"
          >
            Open Tool
          </Link>
        </div>
      </nav>
    </header>
  );
}
