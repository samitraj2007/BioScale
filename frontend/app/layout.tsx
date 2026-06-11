import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import Link from "next/link";

import NavBar from "@/components/NavBar";
import "./globals.css";

const roboto = Roboto({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-roboto",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "BioScale — Phenotypic Age Estimation",
    template: "%s · BioScale",
  },
  description:
    "A personal, end-to-end machine learning and full-stack project by Samit Raj Thapa: phenotypic age estimation from health and lifestyle inputs, with a FastAPI backend and a Next.js frontend.",
  applicationName: "BioScale",
  keywords: [
    "phenotypic age",
    "biological age",
    "machine learning portfolio",
    "FastAPI",
    "Next.js",
    "SHAP",
    "Cox proportional hazards",
  ],
  authors: [{ name: "Samit Raj Thapa" }],
  creator: "Samit Raj Thapa",
  publisher: "University of Wollongong in Dubai",
  openGraph: {
    title: "BioScale — Phenotypic Age Estimation",
    description:
      "A personal ML + full-stack project demonstrating phenotypic age estimation, model explainability, and modern web engineering.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={roboto.variable}>
      <body className="page-bg flex min-h-screen flex-col font-sans antialiased">
        <NavBar />
        <main className="flex-1">{children}</main>

        <footer className="mt-10 border-t border-outline-variant/60 bg-surface-container/60">
          <div className="container-content py-12">
            <div className="grid gap-8 md:grid-cols-3">
              <div className="md:col-span-2">
                <div className="flex items-center gap-2.5">
                  <span
                    aria-hidden
                    className="flex h-9 w-9 items-center justify-center rounded-md-md bg-primary text-title-md font-medium text-on-primary"
                  >
                    B
                  </span>
                  <span className="text-title-md text-on-surface">
                    BioScale — Phenotypic Age Estimation
                  </span>
                </div>
                <p className="mt-3 max-w-md text-body-md text-on-surface-variant">
                  A personal ML + full-stack project by{" "}
                  <span className="font-medium text-on-surface">
                    Samit Raj Thapa
                  </span>{" "}
                  (University of Wollongong in Dubai), built to learn and
                  demonstrate end-to-end data, modeling, backend, and frontend
                  engineering.
                </p>
                <p className="mt-3 max-w-md text-body-sm text-on-surface-variant">
                  This is a learning and portfolio project, not a medical or
                  clinical product.
                </p>
              </div>

              <nav className="flex flex-col gap-3 text-body-md">
                <span className="text-label-md uppercase tracking-wide text-on-surface-variant">
                  Explore
                </span>
                <Link
                  href="/"
                  className="w-fit text-on-surface-variant transition-colors hover:text-primary"
                >
                  Overview
                </Link>
                <Link
                  href="/tool"
                  className="w-fit text-on-surface-variant transition-colors hover:text-primary"
                >
                  Tool
                </Link>
                <Link
                  href="/methods"
                  className="w-fit text-on-surface-variant transition-colors hover:text-primary"
                >
                  Methods
                </Link>
              </nav>
            </div>

            <div className="mt-10 border-t border-outline-variant/50 pt-6 text-body-sm text-on-surface-variant">
              © {new Date().getFullYear()} Samit Raj Thapa — built with Next.js,
              FastAPI, and a Material You–inspired design system.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
