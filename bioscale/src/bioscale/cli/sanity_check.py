"""
Quick, runnable sanity check for the phenotypic age calibration.

Prints phenotypic age and age acceleration for a grid of ages and health
profiles, and asserts the basic invariants. Run from the repo root:

    python -c "import sys; sys.path.insert(0, r'bioscale/src'); \
from bioscale.cli.sanity_check import main; main()"

or, with bioscale/src on PYTHONPATH:

    python -m bioscale.cli.sanity_check
"""

from bioscale.models.calibration import (
    ACCEL_MAX,
    ACCEL_MIN,
    AGE_CEIL,
    AGE_FLOOR,
    calibrate_phenotypic_age,
)

PROFILES = {
    "healthy": {
        "sex": "female", "bmi": 22.0, "sleep_hours": 7.5, "sleep_quality": 5,
        "weekly_exercise_sessions": 6, "diet_quality_score": 9, "stress_level": 2,
        "physical_activity_level": "high", "smoking_status": "never",
        "alcohol_intake_frequency": "never", "has_hypertension": False,
        "has_diabetes": False,
    },
    "neutral": {
        "sex": "male", "bmi": 23.0, "sleep_hours": 7.5, "sleep_quality": 3,
        "weekly_exercise_sessions": 3, "diet_quality_score": 6, "stress_level": 4,
        "physical_activity_level": "moderate", "smoking_status": "never",
        "alcohol_intake_frequency": "monthly", "has_hypertension": False,
        "has_diabetes": False,
    },
    "unhealthy": {
        "sex": "male", "bmi": 38.0, "sleep_hours": 4.5, "sleep_quality": 1,
        "weekly_exercise_sessions": 0, "diet_quality_score": 1, "stress_level": 10,
        "physical_activity_level": "low", "smoking_status": "current",
        "alcohol_intake_frequency": "daily", "has_hypertension": True,
        "has_diabetes": True,
    },
}

AGES = [30, 50, 70, 90, 99]


def main() -> None:
    print(f"{'age':>4} | {'profile':<10} | {'phenotypic':>10} | {'accel':>7}")
    print("-" * 42)

    for age in AGES:
        row_results = {}
        for kind, profile in PROFILES.items():
            r = calibrate_phenotypic_age(age, profile)
            row_results[kind] = r
            print(
                f"{age:>4} | {kind:<10} | {r.phenotypic_age:>10.1f} | "
                f"{r.age_acceleration:>+7.1f}"
            )

            # Invariants.
            assert AGE_FLOOR <= r.phenotypic_age <= AGE_CEIL, "phenotypic age OOB"
            assert ACCEL_MIN - 1e-6 <= r.age_acceleration <= ACCEL_MAX + 1e-6, "accel OOB"

        # Monotonicity at fixed age.
        assert (
            row_results["unhealthy"].phenotypic_age
            > row_results["neutral"].phenotypic_age
            > row_results["healthy"].phenotypic_age
        ), f"monotonicity failed at age {age}"
        print("-" * 42)

    print("\nAll sanity checks passed: bounds respected and unhealthy > healthy.")


if __name__ == "__main__":
    main()
