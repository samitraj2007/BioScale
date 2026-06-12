import type { Metadata } from "next";
import { Pinyon_Script, Roboto } from "next/font/google";
import Link from "next/link";

import NavBar from "@/components/NavBar";
import "./globals.css";

const roboto = Roboto({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-roboto",
  display: "swap",
});

const pinyonScript = Pinyon_Script({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-logo",
  display: "swap",
});

const LINKEDIN_URL = "https://www.linkedin.com/in/samit-raj-thapa";
const GITHUB_URL = "https://github.com/samitraj2007/BioScale";

const socialLinkClassName =
  "inline-flex items-center gap-1.5 text-body-sm text-on-surface-variant transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface";

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
    <html lang="en" className={`${roboto.variable} ${pinyonScript.variable}`}>
      <body className="page-bg flex min-h-screen flex-col font-sans antialiased">
        <NavBar />
        <main className="flex-1">{children}</main>

        <footer className="mt-10 border-t border-outline-variant/60 bg-surface-container/60">
          <div className="container-content py-12">
            <div className="grid gap-8 md:grid-cols-3">
              <div className="md:col-span-2">
                <div className="flex items-center gap-2.5">
                  <span
                    className={`${pinyonScript.className} text-3xl leading-none tracking-tight text-on-primary-container`}
                  >
                    Bioscale
                  </span>
                  <span className="text-title-md text-on-surface">
                    — Phenotypic Age Estimation
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
                <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2">
                  <span className="text-label-md uppercase tracking-wide text-on-surface-variant">
                    Connect
                  </span>
                  <div className="flex flex-wrap items-center gap-3">
                    <a
                      href={LINKEDIN_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="Samit Raj Thapa on LinkedIn"
                      className={socialLinkClassName}
                    >
                      <svg
                        aria-hidden
                        className="h-4 w-4"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                      >
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                      </svg>
                      <span>LinkedIn</span>
                    </a>
                    <a
                      href={GITHUB_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="BioScale source code on GitHub"
                      className={socialLinkClassName}
                    >
                      <svg
                        aria-hidden
                        className="h-4 w-4"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                      >
                        <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.404 1.02.005 2.04.137 3 .404 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
                      </svg>
                      <span>GitHub</span>
                    </a>
                  </div>
                </div>
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
          </div>
        </footer>
      </body>
    </html>
  );
}
