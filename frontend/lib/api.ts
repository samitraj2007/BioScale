/**
 * Client helper for the BioScale FastAPI backend.
 *
 * The base URL is read from NEXT_PUBLIC_API_BASE_URL and defaults to
 * http://localhost:8000 for local development. The request and response
 * shapes mirror the FastAPI `PredictRequest` / `PredictResponse` models.
 */

export type Sex = "male" | "female" | "other" | "unknown";
export type PhysicalActivityLevel = "low" | "moderate" | "high";
export type SmokingStatus = "never" | "former" | "current";
export type AlcoholIntakeFrequency = "never" | "monthly" | "weekly" | "daily";

export interface PredictRequest {
  chronological_age: number;
  sex: Sex;
  bmi: number;
  sleep_hours: number;
  sleep_quality: number;
  weekly_exercise_sessions: number;
  diet_quality_score: number;
  stress_level: number;
  physical_activity_level: PhysicalActivityLevel;
  smoking_status: SmokingStatus;
  alcohol_intake_frequency: AlcoholIntakeFrequency;
  has_hypertension: boolean;
  has_diabetes: boolean;
}

export interface ShapContribution {
  feature: string;
  display_name: string;
  contribution_years: number;
}

export interface ShapSummary {
  top_positive: ShapContribution[];
  top_negative: ShapContribution[];
}

export interface PredictResponse {
  chronological_age: number;
  phenotypic_age: number;
  age_acceleration: number;
  model_version: string;
  /** Optional SHAP feature attributions (present when the backend supplies them). */
  shap_contributions?: ShapSummary;
}

/** Best-effort parse of SHAP contributions; returns undefined if absent/invalid. */
function parseShapContributions(value: unknown): ShapSummary | undefined {
  if (value === null || typeof value !== "object") {
    return undefined;
  }
  const obj = value as Record<string, unknown>;

  const parseList = (list: unknown): ShapContribution[] => {
    if (!Array.isArray(list)) {
      return [];
    }
    return list
      .map((item): ShapContribution | null => {
        if (item === null || typeof item !== "object") {
          return null;
        }
        const entry = item as Record<string, unknown>;
        const contribution = toFiniteNumber(entry.contribution_years);
        if (contribution === null) {
          return null;
        }
        const feature =
          typeof entry.feature === "string" ? entry.feature : "";
        const displayName =
          typeof entry.display_name === "string"
            ? entry.display_name
            : feature || "Feature";
        return {
          feature,
          display_name: displayName,
          contribution_years: contribution,
        };
      })
      .filter((entry): entry is ShapContribution => entry !== null);
  };

  const top_positive = parseList(obj.top_positive);
  const top_negative = parseList(obj.top_negative);

  if (top_positive.length === 0 && top_negative.length === 0) {
    return undefined;
  }
  return { top_positive, top_negative };
}

/** Coerce an unknown value to a finite number, or return null. */
function toFiniteNumber(value: unknown): number | null {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

/**
 * Pick the first key present in `body` whose value coerces to a finite number.
 * Returns the number, or null if none of the candidate keys yield one.
 */
function pickNumber(
  body: Record<string, unknown>,
  keys: readonly string[],
): number | null {
  for (const key of keys) {
    if (key in body) {
      const value = toFiniteNumber(body[key]);
      if (value !== null) {
        return value;
      }
    }
  }
  return null;
}

// Candidate key names emitted by the different BioScale backends.
//  - bioscale/backend/api/app.py        -> "phenotypic_age"
//  - bioscale/src/bioscale/api/main.py  -> "predicted_biological_age"
const PHENOTYPIC_AGE_KEYS = [
  "phenotypic_age",
  "predicted_biological_age",
  "biological_age",
  "phenotypic_age_years",
] as const;
const CHRONOLOGICAL_AGE_KEYS = [
  "chronological_age",
  "chronological_age_years",
] as const;
const AGE_ACCELERATION_KEYS = [
  "age_acceleration",
  "age_acceleration_years",
  "delta_age",
] as const;

/**
 * Validate and normalize a raw `/predict` body into a fully-typed
 * PredictResponse with guaranteed finite numbers. Tolerates the field-name
 * differences between the two BioScale backends and coerces numeric strings.
 * Throws a typed ApiError (with the root cause encoded) if the essential
 * numeric fields are missing or not numeric.
 */
export function normalizePredictResponse(raw: unknown, status = 200): PredictResponse {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    throw new ApiError(
      `The prediction service returned an unexpected response type (${
        Array.isArray(raw) ? "array" : typeof raw
      }); expected a JSON object.`,
      status,
    );
  }

  const body = raw as Record<string, unknown>;

  const phenotypic_age = pickNumber(body, PHENOTYPIC_AGE_KEYS);
  const chronological_age = pickNumber(body, CHRONOLOGICAL_AGE_KEYS);
  let age_acceleration = pickNumber(body, AGE_ACCELERATION_KEYS);

  if (
    age_acceleration === null &&
    phenotypic_age !== null &&
    chronological_age !== null
  ) {
    age_acceleration = phenotypic_age - chronological_age;
  }

  if (
    phenotypic_age === null ||
    chronological_age === null ||
    age_acceleration === null
  ) {
    const missing: string[] = [];
    if (phenotypic_age === null) {
      missing.push(`phenotypic age (any of: ${PHENOTYPIC_AGE_KEYS.join(", ")})`);
    }
    if (chronological_age === null) {
      missing.push(`chronological age (any of: ${CHRONOLOGICAL_AGE_KEYS.join(", ")})`);
    }
    if (age_acceleration === null) {
      missing.push("age acceleration (and it could not be derived)");
    }
    const receivedKeys = Object.keys(body);
    throw new ApiError(
      `The prediction service returned an unexpected response. Missing or non-numeric: ${missing.join(
        "; ",
      )}. Received keys: ${
        receivedKeys.length > 0 ? receivedKeys.join(", ") : "(none)"
      }.`,
      status,
    );
  }

  return {
    phenotypic_age,
    chronological_age,
    age_acceleration,
    model_version:
      typeof body.model_version === "string" && body.model_version.trim() !== ""
        ? body.model_version
        : "unknown",
    shap_contributions: parseShapContributions(body.shap_contributions),
  };
}

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  return raw.replace(/\/+$/, "");
}

/** Error carrying an HTTP status code for nicer UI messaging. */
export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Extract a human-readable message from a FastAPI error body.
 * FastAPI returns `{ detail: string }` or `{ detail: ValidationError[] }`.
 */
function formatDetail(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (item && typeof item === "object") {
          const loc = Array.isArray((item as { loc?: unknown[] }).loc)
            ? (item as { loc: unknown[] }).loc.filter((p) => p !== "body").join(".")
            : "";
          const msg = (item as { msg?: string }).msg ?? "Invalid value";
          return loc ? `${loc}: ${msg}` : msg;
        }
        return null;
      })
      .filter((m): m is string => Boolean(m));
    return messages.length > 0 ? messages.join("; ") : null;
  }
  return null;
}

export async function predict(payload: PredictRequest): Promise<PredictResponse> {
  const url = `${getApiBaseUrl()}/predict`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(
      "Unable to reach the prediction service. Confirm that the backend is running and that NEXT_PUBLIC_API_BASE_URL is configured correctly.",
      0,
    );
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const body = await response.json();
      const detail = formatDetail((body as { detail?: unknown }).detail);
      if (detail) {
        message = detail;
      }
    } catch {
      // Response body was not JSON; keep the default message.
    }
    throw new ApiError(message, response.status);
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new ApiError(
      "The prediction service returned a response that could not be parsed as JSON.",
      response.status,
    );
  }

  return normalizePredictResponse(body, response.status);
}
