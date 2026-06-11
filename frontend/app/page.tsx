import Link from "next/link";

import Blobs from "@/components/Blobs";
import Reveal from "@/components/Reveal";
import SectionHeader from "@/components/SectionHeader";

const techStack = [
  { group: "Frontend", items: ["Next.js 14", "React", "TypeScript", "Tailwind CSS"] },
  { group: "Backend", items: ["Python", "FastAPI", "Pydantic"] },
  { group: "Machine learning", items: ["Cox PH", "XGBoost", "SHAP", "pandas"] },
];

const features = [
  {
    title: "Phenotypic age estimation",
    body: "Estimates biological age from health and lifestyle inputs and contrasts it with chronological age.",
    glyph: "◎",
  },
  {
    title: "Age acceleration",
    body: "Surfaces the gap between phenotypic and chronological age as a single, interpretable number.",
    glyph: "↗",
  },
  {
    title: "Lifestyle-aware regression",
    body: "A gradient-boosted model maps questionnaire-style lifestyle factors onto the phenotypic age scale.",
    glyph: "∿",
  },
  {
    title: "Explainability with SHAP",
    body: "Per-prediction feature attributions show which inputs push an estimate older or younger.",
    glyph: "◈",
  },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="container-content pt-10 sm:pt-16">
        <div className="relative overflow-hidden rounded-md-2xl bg-surface-container px-6 py-14 shadow-md-1 sm:px-12 sm:py-20">
          <Blobs variant="hero" />
          <div className="relative grid items-center gap-12 lg:grid-cols-2">
            <div className="animate-fade-in-up">
              <span className="md-chip-primary">
                <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-primary" />
                Personal ML + full-stack project
              </span>
              <h1 className="mt-5 text-display-md text-on-surface sm:text-display-lg">
                BioScale
                <span className="mt-1 block text-headline-md text-on-surface-variant sm:text-headline-md">
                  Phenotypic Age Estimation
                </span>
              </h1>
              <p className="mt-6 max-w-xl text-body-lg text-on-surface-variant">
                Phenotypic age is a model-based estimate of biological age. BioScale
                predicts it from health and lifestyle inputs, then reports the
                difference from chronological age — a personal project I built to
                demonstrate end-to-end ML, backend, and frontend engineering.
              </p>
              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Link href="/tool" className="btn-filled">
                  Open Tool
                  <span aria-hidden>→</span>
                </Link>
                <Link href="/methods" className="btn-text">
                  View Methods
                </Link>
              </div>
            </div>

            {/* Illustrative card */}
            <div className="group relative animate-fade-in-up lg:justify-self-end">
              {/* Ambient glow that intensifies on hover. */}
              <div
                aria-hidden
                className="absolute -inset-4 -z-10 rounded-md-2xl bg-primary/30 opacity-0 blur-2xl transition-all duration-500 ease-emphasized group-hover:opacity-100 motion-safe:opacity-40 motion-safe:animate-pulse-soft motion-safe:group-hover:opacity-100"
              />
              <div className="md-card md-card-interactive w-full max-w-md p-7 transition-all duration-500 ease-emphasized group-hover:shadow-md-4">
                <div className="flex items-center justify-between">
                  <p className="text-title-md text-on-surface">Example estimate</p>
                  <span className="md-chip">Illustrative</span>
                </div>

                <div className="mt-6 rounded-md-md bg-primary-container p-6">
                  <p className="text-label-md uppercase tracking-wide text-on-primary-container/80">
                    Phenotypic age
                  </p>
                  <p className="mt-1 text-display-md text-on-primary-container">
                    56.2
                    <span className="ml-2 text-title-md font-normal">years</span>
                  </p>
                </div>

                <dl className="mt-5 grid grid-cols-2 gap-3">
                  <div className="md-card-low p-4">
                    <dt className="text-label-md text-on-surface-variant">
                      Chronological
                    </dt>
                    <dd className="mt-1 text-title-lg text-on-surface">52.0</dd>
                  </div>
                  <div className="rounded-md-md bg-tertiary-container p-4">
                    <dt className="text-label-md text-on-tertiary-container/80">
                      Acceleration
                    </dt>
                    <dd className="mt-1 text-title-lg text-on-tertiary-container">
                      +4.2
                    </dd>
                  </div>
                </dl>

                <p className="mt-5 text-body-sm text-on-surface-variant">
                  Illustrative values. Run the tool with your own inputs to obtain
                  a live, model-based estimate.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About this project */}
      <section className="container-content py-16 sm:py-20">
        <Reveal className="grid gap-10 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <SectionHeader
              eyebrow="About this project"
              title="An end-to-end demonstration, built to learn"
            />
            <div className="mt-5 space-y-4 text-body-md text-on-surface-variant">
              <p>
                I built BioScale to practice and showcase the full lifecycle of a
                data product: extracting and harmonizing real-world health survey
                data, engineering a phenotypic age target from survival modeling,
                training a lifestyle regression model, and explaining its
                predictions.
              </p>
              <p>
                The pipeline spans data ETL, a Cox proportional hazards model for
                phenotypic age, a gradient-boosted lifestyle regressor, and
                SHAP-based explanations — served through a FastAPI backend and a
                Next.js, TypeScript, and Tailwind frontend with a Material
                You–inspired design system.
              </p>
              <p className="text-on-surface">
                It is a technical demonstration of my engineering skills, not a
                medical product or clinical tool.
              </p>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="md-card p-6">
              <h3 className="text-title-md text-on-surface">Tech stack</h3>
              <div className="mt-4 space-y-5">
                {techStack.map((stack) => (
                  <div key={stack.group}>
                    <p className="text-label-md uppercase tracking-wide text-on-surface-variant">
                      {stack.group}
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {stack.items.map((item) => (
                        <span key={item} className="md-chip">
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Key capabilities */}
      <section className="container-content pb-16 sm:pb-20">
        <SectionHeader
          eyebrow="Capabilities"
          title="What the project demonstrates"
        />
        <Reveal className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <article key={feature.title} className="md-card md-card-interactive p-6">
              <span
                aria-hidden
                className="flex h-11 w-11 items-center justify-center rounded-md-md bg-secondary-container text-title-lg text-on-secondary-container"
              >
                {feature.glyph}
              </span>
              <h3 className="mt-4 text-title-md text-on-surface">
                {feature.title}
              </h3>
              <p className="mt-2 text-body-sm text-on-surface-variant">
                {feature.body}
              </p>
            </article>
          ))}
        </Reveal>
      </section>

      {/* Disclaimer */}
      <section className="container-content pb-20">
        <div className="md-card relative overflow-hidden bg-tertiary-container p-7 sm:p-9">
          <Blobs variant="soft" />
          <div className="relative">
            <h2 className="text-title-lg text-on-tertiary-container">
              A learning &amp; portfolio project
            </h2>
            <p className="mt-2 max-w-3xl text-body-md text-on-tertiary-container/90">
              This project is for learning and demonstration purposes only. It does
              not provide medical or clinical advice, and its estimates should not
              be used for any health decision.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
