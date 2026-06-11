import type { Metadata } from "next";

import SectionHeader from "@/components/SectionHeader";
import StatCard from "@/components/StatCard";

export const metadata: Metadata = {
  title: "Methods",
  description:
    "How BioScale works: data and ETL, the Cox phenotypic age model, the lifestyle regressor, evaluation metrics, SHAP explainability, and system architecture.",
};

const headlineStats = [
  { label: "Mean absolute error", value: "≈ 4.3 yrs", hint: "Held-out NHANES" },
  { label: "R²", value: "≈ 0.20", hint: "Held-out NHANES" },
  { label: "Survey cycles", value: "1999–2002", hint: "Two NHANES waves" },
];

const performanceRows = [
  { metric: "Mean absolute error (MAE)", value: "≈ 4.3 years", note: "Lower is better" },
  { metric: "Root mean squared error (RMSE)", value: "≈ 6.4 years", note: "Lower is better" },
  { metric: "Coefficient of determination (R²)", value: "≈ 0.20", note: "Higher is better" },
  { metric: "Target variable", value: "Phenotypic age (years)", note: "Cox-derived" },
];

const architecture = [
  { step: "Data & ETL", detail: "NHANES extracts harmonized and linked to mortality." },
  { step: "Models", detail: "Cox PH phenotypic age → lifestyle regressor (XGBoost)." },
  { step: "FastAPI", detail: "/predict serves predictions and SHAP attributions." },
  { step: "Next.js", detail: "TypeScript + Tailwind UI consumes the API." },
];

export default function MethodsPage() {
  return (
    <div className="container-content py-12 sm:py-16">
      <header className="max-w-2xl">
        <p className="eyebrow">How it works</p>
        <h1 className="mt-2 text-headline-md text-on-surface sm:text-display-md">
          Methods &amp; architecture
        </h1>
        <p className="mt-4 text-body-lg text-on-surface-variant">
          A high-level walkthrough of the pipeline behind this project — from raw
          survey data to an explainable prediction served over an API.
        </p>
      </header>

      {/* Headline stats */}
      <div className="mt-10 grid gap-5 sm:grid-cols-3">
        {headlineStats.map((stat) => (
          <StatCard
            key={stat.label}
            label={stat.label}
            value={stat.value}
            hint={stat.hint}
          />
        ))}
      </div>

      {/* Data & ETL */}
      <section className="mt-14">
        <SectionHeader eyebrow="Stage 1" title="Data & preprocessing (ETL)" />
        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          <article className="md-card p-7 lg:col-span-2">
            <div className="space-y-3 text-body-md text-on-surface-variant">
              <p>
                Source data come from the National Health and Nutrition Examination
                Survey (NHANES) 1999–2000 and 2001–2002 cycles. Demographic,
                anthropometric, lifestyle, and laboratory variables are extracted
                from the published survey files and harmonized into a common schema
                across cycles, keyed on the participant identifier (SEQN).
              </p>
              <p>
                Records are linked to public-use mortality follow-up data to obtain
                survival information (follow-up duration and vital status). The ETL
                produces a merged dataset, a model-input dataset of complete
                biomarker cases, and a survival-ready dataset for the phenotypic age
                model.
              </p>
            </div>
          </article>
          <aside className="md-card-low p-7">
            <h3 className="text-title-md text-on-surface">ETL outputs</h3>
            <ul className="mt-4 space-y-4 text-body-sm">
              <li>
                <span className="font-medium text-on-surface">Merged dataset</span>
                <span className="mt-0.5 block text-on-surface-variant">
                  Harmonized variables across both cycles.
                </span>
              </li>
              <li>
                <span className="font-medium text-on-surface">Model input</span>
                <span className="mt-0.5 block text-on-surface-variant">
                  Complete biomarker cases used for modeling.
                </span>
              </li>
              <li>
                <span className="font-medium text-on-surface">
                  Survival-ready dataset
                </span>
                <span className="mt-0.5 block text-on-surface-variant">
                  Mortality-linked follow-up and event indicator.
                </span>
              </li>
            </ul>
          </aside>
        </div>
      </section>

      {/* Phenotypic age model */}
      <section className="mt-14">
        <SectionHeader eyebrow="Stage 2" title="Phenotypic age model" />
        <article className="md-card mt-6 p-7">
          <div className="space-y-3 text-body-md text-on-surface-variant">
            <p>
              A penalized Cox proportional hazards model is fitted on clinical
              biomarkers together with chronological age to estimate mortality
              hazard. The model&apos;s linear predictor summarizes relative
              mortality risk for each participant.
            </p>
            <p>
              That risk is mapped onto a continuous phenotypic age scale, in years,
              via a deterministic monotonic transformation. The resulting
              phenotypic age is the training target for the lifestyle model. It is
              an engineered, biomarker-calibrated approximation of biological age,
              not a reproduction of any specific published coefficient set.
            </p>
          </div>
        </article>
      </section>

      {/* Lifestyle regressor */}
      <section className="mt-14">
        <SectionHeader eyebrow="Stage 3" title="Lifestyle regression model" />
        <article className="md-card mt-6 p-7">
          <div className="space-y-3 text-body-md text-on-surface-variant">
            <p>
              A gradient-boosted regression model (XGBoost) predicts phenotypic age
              from lifestyle and health factors: chronological age, BMI, sleep,
              physical activity, diet quality, perceived stress, smoking, alcohol
              intake, and selected clinical conditions. Numeric features are
              standardized and categorical features one-hot encoded within a single
              preprocessing pipeline; hyperparameters are chosen by cross-validated
              optimization.
            </p>
            <p>
              On held-out NHANES data, the model reaches an MAE of roughly 4.3 years
              and R² of roughly 0.20 — reflecting the limited signal available from
              questionnaire-style lifestyle features relative to direct biomarker
              measurement.
            </p>
          </div>
        </article>
      </section>

      {/* Performance */}
      <section className="mt-14">
        <SectionHeader
          eyebrow="Evaluation"
          title="Performance metrics"
          description="Approximate held-out metrics for the lifestyle regressor."
        />
        <div className="md-card mt-6 overflow-hidden">
          <table className="w-full text-left text-body-md">
            <caption className="sr-only">
              Held-out performance metrics for the lifestyle regressor.
            </caption>
            <thead className="bg-surface-container-low text-on-surface-variant">
              <tr>
                <th scope="col" className="px-6 py-3 text-label-md font-medium">
                  Metric
                </th>
                <th scope="col" className="px-6 py-3 text-label-md font-medium">
                  Held-out value
                </th>
                <th
                  scope="col"
                  className="hidden px-6 py-3 text-label-md font-medium sm:table-cell"
                >
                  Direction
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/40">
              {performanceRows.map((row) => (
                <tr
                  key={row.metric}
                  className="transition-colors hover:bg-surface-container-low/50"
                >
                  <td className="px-6 py-4 text-on-surface-variant">
                    {row.metric}
                  </td>
                  <td className="px-6 py-4 font-medium text-on-surface">
                    {row.value}
                  </td>
                  <td className="hidden px-6 py-4 text-on-surface-variant sm:table-cell">
                    {row.note}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-body-sm text-on-surface-variant">
          Metrics are approximate and depend on the specific training run, data
          split, and hyperparameter configuration.
        </p>
      </section>

      {/* Explainability */}
      <section className="mt-14">
        <SectionHeader eyebrow="Interpretability" title="Explainability with SHAP" />
        <article className="md-card mt-6 p-7">
          <div className="space-y-3 text-body-md text-on-surface-variant">
            <p>
              SHAP (SHapley Additive exPlanations) attributes a prediction to its
              input features by estimating each feature&apos;s contribution
              relative to a baseline. For a given estimate, this reveals which
              inputs push the predicted phenotypic age older or younger.
            </p>
            <p>
              The API returns the top positive and negative contributors with each
              prediction, and the tool surfaces them as a concise &ldquo;Top
              drivers&rdquo; summary — turning an opaque number into an inspectable
              result.
            </p>
          </div>
        </article>
      </section>

      {/* Architecture */}
      <section className="mt-14">
        <SectionHeader
          eyebrow="System design"
          title="Architecture"
          description="Data flows from ingestion through modeling to an explainable API and a typed frontend."
        />
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {architecture.map((node, index) => (
            <div key={node.step} className="md-card md-card-interactive p-6">
              <span className="text-label-md text-on-surface-variant">
                Step {index + 1}
              </span>
              <h3 className="mt-1 text-title-md text-on-surface">{node.step}</h3>
              <p className="mt-2 text-body-sm text-on-surface-variant">
                {node.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer */}
      <section className="mt-14">
        <article className="md-card bg-tertiary-container p-7">
          <h2 className="text-title-md text-on-tertiary-container">
            Interpretation &amp; limitations
          </h2>
          <p className="mt-2 text-body-md text-on-tertiary-container/90">
            Estimates derive from cross-sectional survey data and an engineered
            target. They describe population-level associations, not individual
            clinical status, and are presented as a learning and portfolio project
            — not medical advice.
          </p>
        </article>
      </section>
    </div>
  );
}
