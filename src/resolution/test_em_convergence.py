import os
import sys
import pandas as pd
import numpy as np

# Allow importing bayesian_em.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import bayesian_em


def test_em_convergence_behavior():

    print("=" * 80)
    print("EM CONVERGENCE ANALYSIS")
    print("=" * 80)

    input_path = "data/processed/reliability_scored_records.csv"

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Required file not found: {input_path}\n"
            "Run reliability_scorer.py first."
        )

    df = pd.read_csv(
        input_path,
        low_memory=False
    )

    df["cadre"] = (
        df["cadre"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    results = []

    # Test one representative numeric field from each domain.
    test_fields = {
    "maternal": "haemoglobin_gdl",
    "child": "muac_cm",
    "chronic": "fasting_blood_sugar",
    }

    for domain, field in test_fields.items():

        print(f"\nTesting domain: {domain}")
        print(f"Field: {field}")

        domain_df = df[df["domain"] == domain]

        if field not in domain_df.columns:
            print(f"Field {field} not found. Skipping.")
            continue

        groups = domain_df.groupby("patient_id")

        tested = 0

        for patient_id, group in groups:

            if tested >= 100:
                break

            if group[field].notna().sum() < 2:
                continue

            # Run the existing EM implementation.
            truth = bayesian_em.run_em(
                group,
                field
            )

            results.append({
                "domain": domain,
                "field": field,
                "patient_id": patient_id,
                "final_truth": truth,
                "max_iterations": bayesian_em.MAX_ITERATIONS,
                "convergence_threshold":
                    bayesian_em.CONVERGENCE_THRESHOLD
            })

            tested += 1

        print(f"Groups tested: {tested}")

    results_df = pd.DataFrame(results)

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    output_path = (
        "data/processed/"
        "em_convergence_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print("\n" + "=" * 80)
    print("EM CONVERGENCE TEST SUMMARY")
    print("=" * 80)

    print(
        f"Total EM runs tested: "
        f"{len(results_df)}"
    )

    print(
        f"Maximum iterations configured: "
        f"{bayesian_em.MAX_ITERATIONS}"
    )

    print(
        f"Convergence threshold configured: "
        f"{bayesian_em.CONVERGENCE_THRESHOLD}"
    )

    if not results_df.empty:

        print("\nRuns by domain:")

        print(
            results_df["domain"]
            .value_counts()
            .to_string()
        )

    print(
        f"\nResults saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    test_em_convergence_behavior()
