"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

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
    <header className="sticky top-0 z-40 border-b border-outline-variant/40 bg-surface/70 backdrop-blur-xl">
      <nav className="container-content flex h-16 items-center justify-between">
        <Link href="/" className="group flex items-center gap-2.5">
          <span
            aria-hidden
            className="flex h-9 w-9 items-center justify-center rounded-md-md bg-primary text-title-md font-medium text-on-primary shadow-md-1 transition-transform duration-300 ease-emphasized group-hover:scale-105"
          >
            B
          </span>
          <span className="text-title-md text-on-surface">BioScale</span>
        </Link>

        <div className="flex items-center gap-1 sm:gap-2">
          <ul className="flex items-center gap-1">
            {links.map((link) => {
              const active = isActive(pathname, link.href);
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    aria-current={active ? "page" : undefined}
                    className={[
                      "state-layer rounded-full px-3 py-2 text-label-lg transition-colors duration-200 sm:px-4",
                      active
                        ? "bg-secondary-container text-on-secondary-container"
                        : "text-on-surface-variant hover:text-on-surface",
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
            className="btn-filled hidden px-5 py-2.5 sm:inline-flex"
          >
            Open Tool
          </Link>
        </div>
      </nav>
    </header>
  );
}
