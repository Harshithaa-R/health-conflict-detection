import os
import sys
import pandas as pd
import numpy as np

# Allow importing bayesian_em.py when this file is run directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from bayesian_em import run_em


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

TOLERANCES = [1e-2, 1e-3, 1e-4, 1e-5]
MAX_ITERATIONS = 20


# ---------------------------------------------------------
# FIND ITERATION / CONVERGENCE INFORMATION
# ---------------------------------------------------------

def run_convergence_test(tolerance):

    print(f"\nTesting tolerance: {tolerance}")

    # Run EM with the selected tolerance.
    # The actual bayesian_em implementation remains the
    # source of truth for the EM calculation.
    try:
        result = run_em(
            tolerance=tolerance,
            max_iterations=MAX_ITERATIONS
        )
    except TypeError:
        # If the existing function uses different parameter
        # names, report that clearly rather than changing it.
        print(
            "WARNING: run_em() does not accept "
            "tolerance/max_iterations arguments."
        )
        return {
            "Tolerance": tolerance,
            "Max_Iterations": MAX_ITERATIONS,
            "Status": "MANUAL_CHECK_REQUIRED"
        }

    # Try to extract useful convergence information
    # from the returned result.
    iterations = MAX_ITERATIONS
    converged = None
    rmse = None

    if isinstance(result, dict):

        if "iterations" in result:
            iterations = result["iterations"]

        elif "n_iterations" in result:
            iterations = result["n_iterations"]

        elif "num_iterations" in result:
            iterations = result["num_iterations"]

        if "converged" in result:
            converged = result["converged"]

        if "rmse" in result:
            rmse = result["rmse"]

        elif "final_rmse" in result:
            rmse = result["final_rmse"]

    elif isinstance(result, pd.DataFrame):

        # Look for convergence-related columns
        columns_lower = {
            str(c).lower(): c
            for c in result.columns
        }

        for key in [
            "iterations",
            "n_iterations",
            "num_iterations"
        ]:
            if key in columns_lower:
                iterations = result[columns_lower[key]].iloc[0]
                break

        for key in [
            "rmse",
            "final_rmse"
        ]:
            if key in columns_lower:
                rmse = result[columns_lower[key]].iloc[0]
                break

    return {
        "Tolerance": tolerance,
        "Max_Iterations": MAX_ITERATIONS,
        "Iterations": iterations,
        "Converged": converged,
        "RMSE": rmse,
        "Status": "COMPLETED"
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 90)
    print("EM CONVERGENCE AND TOLERANCE ANALYSIS")
    print("=" * 90)

    results = []

    for tolerance in TOLERANCES:

        result = run_convergence_test(tolerance)

        results.append(result)

    results_df = pd.DataFrame(results)

    print("\n")
    print("=" * 90)
    print("EM CONVERGENCE RESULTS")
    print("=" * 90)

    print(results_df.to_string(index=False))

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

    print("=" * 90)
    print(f"Results saved to: {output_path}")
    print("=" * 90)


if __name__ == "__main__":
    main()