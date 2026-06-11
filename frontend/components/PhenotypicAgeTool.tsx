"use client";

import { useState } from "react";

import {
  ApiError,
  predict,
  type PredictRequest,
  type PredictResponse,
  type ShapContribution,
} from "@/lib/api";

/** Return the value only if it is a finite number, otherwise null. */
function toFiniteOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** Format a possibly-missing number to 1 decimal, or a safe placeholder. */
function formatNumber(value: number | null, fractionDigits = 1): string {
  return value === null ? "–" : value.toFixed(fractionDigits);
}

// Raw string defaults for the numeric inputs. Numeric fields store *exactly*
// what the user typed (a string) so values can never "jump" mid-edit (e.g.
// "7." or "0" being snapped to another number). Parsing/clamping happens only
// in the submit handler when the JSON payload is built.
const numericDefaults = {
  chronological_age: "52",
  bmi: "26.5",
  sleep_hours: "7",
  sleep_quality: "3",
  weekly_exercise_sessions: "3",
  diet_quality_score: "6",
  stress_level: "5",
} as const;

type NumericField = keyof typeof numericDefaults;
type NumericState = Record<NumericField, string>;

// Non-numeric fields (selects / booleans) keep their typed values directly;
// these controls cannot exhibit the numeric "jump" problem.
type ChoiceState = Pick<
  PredictRequest,
  | "sex"
  | "physical_activity_level"
  | "smoking_status"
  | "alcohol_intake_frequency"
  | "has_hypertension"
  | "has_diabetes"
>;

const choiceDefaults: ChoiceState = {
  sex: "male",
  physical_activity_level: "moderate",
  smoking_status: "never",
  alcohol_intake_frequency: "monthly",
  has_hypertension: false,
  has_diabetes: false,
};

// Fallbacks used only if a field is somehow empty/non-numeric at submit time
// (HTML `required` + min/max validation normally prevents this).
const numericFallbacks: Record<NumericField, number> = {
  chronological_age: 18,
  bmi: 25,
  sleep_hours: 7,
  sleep_quality: 3,
  weekly_exercise_sessions: 3,
  diet_quality_score: 5,
  stress_level: 5,
};

/** Parse a raw input string to a finite number, or fall back. No clamping. */
function parseRaw(raw: string, fallback: number): number {
  const n = Number(raw);
  return raw.trim() !== "" && Number.isFinite(n) ? n : fallback;
}

type Status = "idle" | "loading" | "success" | "error";

// ---------------------------------------------------------------------------
// Presentational helpers
// ---------------------------------------------------------------------------

function FormSection({
  step,
  title,
  description,
  children,
}: {
  step: number;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <fieldset>
      <legend className="mb-4 flex items-center gap-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary-container text-label-md text-on-secondary-container">
          {step}
        </span>
        <span>
          <span className="block text-title-md text-on-surface">{title}</span>
          <span className="block text-body-sm text-on-surface-variant">
            {description}
          </span>
        </span>
      </legend>
      <div className="grid gap-x-5 gap-y-5 sm:grid-cols-2">{children}</div>
    </fieldset>
  );
}

function Field({
  label,
  htmlFor,
  hint,
  children,
}: {
  label: string;
  htmlFor: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label htmlFor={htmlFor} className="md-label">
        {label}
      </label>
      {children}
      {hint && <p className="md-hint">{hint}</p>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function PhenotypicAgeTool() {
  const [numbers, setNumbers] = useState<NumericState>({ ...numericDefaults });
  const [choices, setChoices] = useState<ChoiceState>(choiceDefaults);
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // The clamped chronological age actually submitted; rendered in the results
  // card so the "Chronological" number always matches what was sent.
  const [submittedAge, setSubmittedAge] = useState<number | null>(null);
  // Bumped on every successful prediction so result animations re-trigger.
  const [predictionId, setPredictionId] = useState(0);

  // Numeric inputs store the raw typed string verbatim — no parsing, scaling,
  // or clamping here, so the visible value never changes on its own.
  function updateNumber(key: NumericField, raw: string) {
    setNumbers((prev) => ({ ...prev, [key]: raw }));
  }

  function updateChoice<K extends keyof ChoiceState>(
    key: K,
    value: ChoiceState[K],
  ) {
    setChoices((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setErrorMessage(null);

    // All domain logic (parsing + clamping) happens here, never in onChange.
    // Chronological age is clamped to the supported range [18, 150]; the same
    // value is both submitted and shown as "Chronological".
    const age = Math.min(
      Math.max(
        parseRaw(numbers.chronological_age, numericFallbacks.chronological_age),
        18,
      ),
      150,
    );
    const payload: PredictRequest = {
      chronological_age: age,
      bmi: parseRaw(numbers.bmi, numericFallbacks.bmi),
      sleep_hours: parseRaw(numbers.sleep_hours, numericFallbacks.sleep_hours),
      sleep_quality: parseRaw(
        numbers.sleep_quality,
        numericFallbacks.sleep_quality,
      ),
      weekly_exercise_sessions: parseRaw(
        numbers.weekly_exercise_sessions,
        numericFallbacks.weekly_exercise_sessions,
      ),
      diet_quality_score: parseRaw(
        numbers.diet_quality_score,
        numericFallbacks.diet_quality_score,
      ),
      stress_level: parseRaw(
        numbers.stress_level,
        numericFallbacks.stress_level,
      ),
      ...choices,
    };
    setSubmittedAge(age);

    try {
      const response = await predict(payload);
      setResult(response);
      setStatus("success");
      setPredictionId((id) => id + 1);
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred while requesting a prediction.";
      setErrorMessage(message);
      setStatus("error");
    }
  }

  function handleReset() {
    setNumbers({ ...numericDefaults });
    setChoices(choiceDefaults);
    setResult(null);
    setStatus("idle");
    setErrorMessage(null);
    setSubmittedAge(null);
  }

  return (
    <div className="grid gap-8 lg:grid-cols-5">
      {/* Form column */}
      <section className="lg:col-span-3">
        <form onSubmit={handleSubmit} className="md-card p-6 sm:p-8">
          <div className="mb-8">
            <h2 className="text-title-lg text-on-surface">Input features</h2>
            <p className="mt-1 text-body-sm text-on-surface-variant">
              All fields are required. Values are passed to the model exactly as
              entered.
            </p>
          </div>

          <div className="space-y-10">
            {/* 1. Demographics */}
            <FormSection
              step={1}
              title="Demographics"
              description="Baseline characteristics"
            >
              <Field
                label="Chronological age"
                htmlFor="chronological_age"
                hint="Age 18–150 years. Values below 18 are not supported."
              >
                <input
                  id="chronological_age"
                  type="number"
                  min={18}
                  max={150}
                  step={1}
                  required
                  className="md-field"
                  value={numbers.chronological_age}
                  onChange={(e) =>
                    updateNumber("chronological_age", e.target.value)
                  }
                />
              </Field>
              <Field label="Sex" htmlFor="sex">
                <select
                  id="sex"
                  className="md-field"
                  value={choices.sex}
                  onChange={(e) =>
                    updateChoice("sex", e.target.value as PredictRequest["sex"])
                  }
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="unknown">Unknown</option>
                </select>
              </Field>
            </FormSection>

            {/* 2. Lifestyle */}
            <FormSection
              step={2}
              title="Lifestyle"
              description="Behavior and daily habits"
            >
              <Field
                label="Average sleep"
                htmlFor="sleep_hours"
                hint="Hours per night, 0–24"
              >
                <input
                  id="sleep_hours"
                  type="number"
                  min={0}
                  max={24}
                  step={0.5}
                  required
                  className="md-field"
                  value={numbers.sleep_hours}
                  onChange={(e) => updateNumber("sleep_hours", e.target.value)}
                />
              </Field>
              <Field
                label="Sleep quality"
                htmlFor="sleep_quality"
                hint="Scale 1–5, higher is better"
              >
                <input
                  id="sleep_quality"
                  type="number"
                  min={1}
                  max={5}
                  step={1}
                  required
                  className="md-field"
                  value={numbers.sleep_quality}
                  onChange={(e) => updateNumber("sleep_quality", e.target.value)}
                />
              </Field>
              <Field
                label="Physical activity level"
                htmlFor="physical_activity_level"
              >
                <select
                  id="physical_activity_level"
                  className="md-field"
                  value={choices.physical_activity_level}
                  onChange={(e) =>
                    updateChoice(
                      "physical_activity_level",
                      e.target
                        .value as PredictRequest["physical_activity_level"],
                    )
                  }
                >
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                </select>
              </Field>
              <Field
                label="Weekly exercise sessions"
                htmlFor="weekly_exercise_sessions"
                hint="Count per week, 0–7"
              >
                <input
                  id="weekly_exercise_sessions"
                  type="number"
                  min={0}
                  max={7}
                  step={1}
                  required
                  className="md-field"
                  value={numbers.weekly_exercise_sessions}
                  onChange={(e) =>
                    updateNumber("weekly_exercise_sessions", e.target.value)
                  }
                />
              </Field>
              <Field
                label="Diet quality score"
                htmlFor="diet_quality_score"
                hint="Scale 1–10, higher is better"
              >
                <input
                  id="diet_quality_score"
                  type="number"
                  min={1}
                  max={10}
                  step={1}
                  required
                  className="md-field"
                  value={numbers.diet_quality_score}
                  onChange={(e) =>
                    updateNumber("diet_quality_score", e.target.value)
                  }
                />
              </Field>
              <Field
                label="Stress level"
                htmlFor="stress_level"
                hint="Scale 1–10, higher is more stress"
              >
                <input
                  id="stress_level"
                  type="number"
                  min={1}
                  max={10}
                  step={1}
                  required
                  className="md-field"
                  value={numbers.stress_level}
                  onChange={(e) => updateNumber("stress_level", e.target.value)}
                />
              </Field>
              <Field label="Smoking status" htmlFor="smoking_status">
                <select
                  id="smoking_status"
                  className="md-field"
                  value={choices.smoking_status}
                  onChange={(e) =>
                    updateChoice(
                      "smoking_status",
                      e.target.value as PredictRequest["smoking_status"],
                    )
                  }
                >
                  <option value="never">Never</option>
                  <option value="former">Former</option>
                  <option value="current">Current</option>
                </select>
              </Field>
              <Field
                label="Alcohol intake frequency"
                htmlFor="alcohol_intake_frequency"
              >
                <select
                  id="alcohol_intake_frequency"
                  className="md-field"
                  value={choices.alcohol_intake_frequency}
                  onChange={(e) =>
                    updateChoice(
                      "alcohol_intake_frequency",
                      e.target
                        .value as PredictRequest["alcohol_intake_frequency"],
                    )
                  }
                >
                  <option value="never">Never</option>
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                  <option value="daily">Daily</option>
                </select>
              </Field>
            </FormSection>

            {/* 3. Clinical & anthropometric */}
            <FormSection
              step={3}
              title="Clinical & anthropometric"
              description="Body measures and diagnosed conditions"
            >
              <Field
                label="Body mass index"
                htmlFor="bmi"
                hint="kg/m², typically 10–60"
              >
                <input
                  id="bmi"
                  type="number"
                  min={10}
                  max={60}
                  step={0.1}
                  required
                  className="md-field"
                  value={numbers.bmi}
                  onChange={(e) => updateNumber("bmi", e.target.value)}
                />
              </Field>
              <div className="hidden sm:block" aria-hidden />
              <Field label="Diagnosed hypertension" htmlFor="has_hypertension">
                <select
                  id="has_hypertension"
                  className="md-field"
                  value={choices.has_hypertension ? "yes" : "no"}
                  onChange={(e) =>
                    updateChoice("has_hypertension", e.target.value === "yes")
                  }
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </Field>
              <Field label="Diagnosed diabetes" htmlFor="has_diabetes">
                <select
                  id="has_diabetes"
                  className="md-field"
                  value={choices.has_diabetes ? "yes" : "no"}
                  onChange={(e) =>
                    updateChoice("has_diabetes", e.target.value === "yes")
                  }
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </Field>
            </FormSection>
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-outline-variant/50 pt-6">
            <button
              type="submit"
              className="btn-filled"
              disabled={status === "loading"}
            >
              {status === "loading" ? (
                <>
                  <span
                    aria-hidden
                    className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/40 border-t-on-primary"
                  />
                  Estimating…
                </>
              ) : (
                "Estimate phenotypic age"
              )}
            </button>
            <button type="button" className="btn-tonal" onClick={handleReset}>
              Reset
            </button>
          </div>
        </form>
      </section>

      {/* Results column */}
      <section className="lg:col-span-2">
        <div className="lg:sticky lg:top-24">
          <ResultsPanel
            status={status}
            result={result}
            errorMessage={errorMessage}
            submittedAge={submittedAge}
            predictionId={predictionId}
          />
        </div>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Results panel
// ---------------------------------------------------------------------------

function DriverChips({
  title,
  items,
}: {
  title: string;
  items: ShapContribution[];
}) {
  if (items.length === 0) {
    return null;
  }
  return (
    <div>
      <p className="text-label-md uppercase tracking-wide text-on-surface-variant">
        {title}
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {items.map((item) => {
          const v = toFiniteOrNull(item.contribution_years);
          const sign = v === null ? "" : v >= 0 ? "+" : "−";
          return (
            <span key={`${title}-${item.feature}`} className="md-chip">
              {item.display_name}
              <span className="text-on-surface">
                {sign}
                {formatNumber(v === null ? null : Math.abs(v))} yr
              </span>
            </span>
          );
        })}
      </div>
    </div>
  );
}

function ResultsPanel({
  status,
  result,
  errorMessage,
  submittedAge,
  predictionId,
}: {
  status: Status;
  result: PredictResponse | null;
  errorMessage: string | null;
  submittedAge: number | null;
  predictionId: number;
}) {
  if (status === "error") {
    return (
      <div className="md-card overflow-hidden bg-error-container p-6">
        <div className="flex items-center gap-2">
          <span
            aria-hidden
            className="flex h-6 w-6 items-center justify-center rounded-full bg-error text-label-md text-white"
          >
            !
          </span>
          <h2 className="text-title-md text-on-error-container">
            Request failed
          </h2>
        </div>
        <p className="mt-3 text-body-sm leading-relaxed text-on-error-container">
          {errorMessage}
        </p>
        <p className="mt-4 border-t border-on-error-container/20 pt-4 text-body-sm text-on-error-container/80">
          Confirm the backend is running and that the API base URL is configured
          correctly, then try again.
        </p>
      </div>
    );
  }

  if (status === "loading") {
    return (
      <div className="md-card p-6">
        <div className="flex items-center gap-3">
          <span
            aria-hidden
            className="h-5 w-5 animate-spin rounded-full border-2 border-outline-variant border-t-primary"
          />
          <h2 className="text-title-md text-on-surface">Estimating</h2>
        </div>
        <div className="mt-6 space-y-3" aria-hidden>
          <div className="h-14 w-40 animate-pulse rounded-md-md bg-surface-container-low" />
          <div className="h-4 w-full animate-pulse rounded-full bg-surface-container-low" />
          <div className="h-4 w-2/3 animate-pulse rounded-full bg-surface-container-low" />
        </div>
        <p className="mt-4 text-body-sm text-on-surface-variant">
          Submitting features to the prediction service…
        </p>
      </div>
    );
  }

  if (status === "success" && result) {
    const phenotypicAge = toFiniteOrNull(result.phenotypic_age);
    // Prefer the clamped age the user actually submitted so the displayed
    // "Chronological" value always matches the input (e.g. 25 -> 25.0), never
    // a value reconstructed from the response.
    const chronologicalAge =
      toFiniteOrNull(submittedAge) ?? toFiniteOrNull(result.chronological_age);
    const delta = toFiniteOrNull(result.age_acceleration);
    const shap = result.shap_contributions;

    const comparison =
      delta === null
        ? "The age difference is unavailable for this result."
        : Math.abs(delta) < 0.05
          ? "Phenotypic age is approximately equal to chronological age."
          : delta > 0
            ? `Phenotypic age is ${Math.abs(delta).toFixed(1)} years higher than chronological age.`
            : `Phenotypic age is ${Math.abs(delta).toFixed(1)} years lower than chronological age.`;

    return (
      <div className="md-card overflow-hidden">
        <div className="bg-primary-container p-6">
          <h2 className="text-label-md uppercase tracking-wide text-on-primary-container/80">
            Estimated phenotypic age
          </h2>
          <p
            key={predictionId}
            className="mt-2 text-display-md text-on-primary-container motion-safe:animate-result-pop"
          >
            {formatNumber(phenotypicAge)}
            <span className="ml-2 text-title-lg font-normal">years</span>
          </p>
        </div>

        <div className="p-6">
          <dl className="grid grid-cols-2 gap-3">
            <div className="md-card-low p-4">
              <dt className="text-label-md text-on-surface-variant">
                Chronological
              </dt>
              <dd className="mt-1 text-title-lg text-on-surface">
                {formatNumber(chronologicalAge)}
                <span className="ml-1 text-body-sm text-on-surface-variant">
                  yrs
                </span>
              </dd>
            </div>
            <div
              key={predictionId}
              className="rounded-md-md bg-tertiary-container p-4 motion-safe:animate-badge-pop"
            >
              <dt className="text-label-md text-on-tertiary-container/80">
                Age acceleration
              </dt>
              <dd className="mt-1 text-title-lg text-on-tertiary-container">
                {delta === null
                  ? "–"
                  : `${delta >= 0 ? "+" : "−"}${Math.abs(delta).toFixed(1)}`}
                <span className="ml-1 text-body-sm">yrs</span>
              </dd>
            </div>
          </dl>

          <p className="mt-4 text-body-md text-on-surface-variant">
            {comparison}
          </p>

          {shap && (shap.top_positive.length > 0 || shap.top_negative.length > 0) && (
            <div className="mt-5 space-y-4 border-t border-outline-variant/50 pt-5">
              <p className="text-title-md text-on-surface">Top drivers</p>
              <DriverChips title="Pushes older" items={shap.top_positive} />
              <DriverChips title="Pushes younger" items={shap.top_negative} />
            </div>
          )}

          <div className="mt-5 flex items-center justify-between border-t border-outline-variant/50 pt-4">
            <span className="text-body-sm text-on-surface-variant">
              Model version
            </span>
            <span className="md-chip">{result.model_version || "unknown"}</span>
          </div>

          <p className="mt-4 text-body-sm text-on-surface-variant">
            Model-based estimate from a learning project. Not a clinical
            measurement and not for medical decisions.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="md-card p-6">
      <h2 className="text-title-md text-on-surface">Results</h2>
      <div className="mt-4 rounded-md-md border border-dashed border-outline-variant bg-surface-container-low/60 p-6 text-center">
        <p className="text-body-sm text-on-surface-variant">
          Complete the form and select{" "}
          <span className="font-medium text-on-surface">
            Estimate phenotypic age
          </span>{" "}
          to request a prediction.
        </p>
      </div>
      <p className="mt-4 text-body-sm text-on-surface-variant">
        The estimated phenotypic age, chronological age, and their difference
        will appear here.
      </p>
    </div>
  );
}
