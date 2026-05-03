"""
generate_dataset.py
===================
Synthetic health record generator using NFHS-5 Karnataka distributions.

Generates multi-source patient records that simulate the CHW ecosystem
(ASHA, ANM, AWW, PHC, CHC, District Hospital) with realistic conflicts
injected according to field-level conflict rates from the literature.

Usage:
    python scripts/generate_dataset.py --n_patients 50000 --output data/synthetic/
    python scripts/generate_dataset.py --n_patients 1000 --output data/synthetic/ --seed 42
"""

import argparse
import json
import os
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

SOURCES = ["asha", "anm", "aww", "phc_doctor", "chc", "district_hospital"]

SOURCE_RELIABILITY = {
    "phc_doctor":        0.95,
    "anm":               0.88,
    "asha":              0.74,
    "aww":               0.71,
    "district_hospital": 0.97,
    "chc":               0.93,
}

DATA_ENTRY_DELAY = {
    "asha":              (4.2, 3.1),
    "anm":               (1.8, 1.4),
    "aww":               (6.1, 4.8),
    "phc_doctor":        (0.3, 0.5),
    "chc":               (0.5, 0.8),
    "district_hospital": (0.2, 0.4),
}

KARNATAKA_DISTRICTS = {
    "high_burden":   ["Kalaburagi", "Yadgir", "Raichur", "Koppal", "Ballari"],
    "medium_burden": ["Vijayapura", "Bidar", "Haveri", "Gadag", "Chitradurga"],
    "low_burden":    ["Dakshina Kannada", "Udupi", "Kodagu", "Bengaluru Rural", "Tumkur"],
}
ALL_DISTRICTS = [d for dlist in KARNATAKA_DISTRICTS.values() for d in dlist]

DISTRICT_BURDEN = {
    **{d: "high"   for d in KARNATAKA_DISTRICTS["high_burden"]},
    **{d: "medium" for d in KARNATAKA_DISTRICTS["medium_burden"]},
    **{d: "low"    for d in KARNATAKA_DISTRICTS["low_burden"]},
}

DISTRICT_ANAEMIA_ADJ = {
    "Kalaburagi": +0.08, "Yadgir": +0.11, "Raichur": +0.09,
    "Dakshina Kannada": -0.06, "Udupi": -0.07,
}

IMMUNIZATION_SCHEDULE_DAYS = {
    "BCG": (3, 5), "OPV0": (3, 5),
    "DPT1": (48, 14), "DPT2": (76, 14), "DPT3": (104, 14),
    "MR1": (275, 21),
}

CONFLICT_TYPE_WEIGHTS = {
    "numeric_outlier":             0.28,
    "categorical_mismatch":        0.22,
    "temporal_inconsistency":      0.19,
    "demographic_drift":           0.14,
    "physiological_impossibility": 0.09,
    "cross_field_contradiction":   0.08,
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────

rng = np.random.default_rng()


def set_seed(seed: int):
    global rng
    rng = np.random.default_rng(seed)
    random.seed(seed)
    np.random.seed(seed)


def sample_district() -> str:
    weights = [0.35, 0.40, 0.25]  # high / medium / low burden
    tier = random.choices(["high_burden", "medium_burden", "low_burden"], weights=weights)[0]
    return random.choice(KARNATAKA_DISTRICTS[tier])


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=int(rng.integers(0, delta + 1)))


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


# ──────────────────────────────────────────────────────────────────────────────
# Ground-truth patient generator (based on NFHS-5 Karnataka)
# ──────────────────────────────────────────────────────────────────────────────

def generate_ground_truth(patient_id: str, district: str) -> dict:
    """Generate a single patient's true health profile."""
    anaemia_adj = DISTRICT_ANAEMIA_ADJ.get(district, 0.0)

    # Demographics
    age = int(rng.integers(15, 50))
    dob = date.today() - timedelta(days=age * 365 + int(rng.integers(0, 365)))
    is_pregnant = (age <= 35) and (rng.random() < 0.08)

    # Anthropometry — NFHS-5 BMI distribution
    bmi_category = rng.choice(
        ["underweight", "normal", "overweight", "obese"],
        p=[0.212, 0.521, 0.168, 0.099]
    )
    bmi_ranges = {
        "underweight": (13.0, 18.4),
        "normal":      (18.5, 24.9),
        "overweight":  (25.0, 29.9),
        "obese":       (30.0, 42.0),
    }
    bmi = float(rng.uniform(*bmi_ranges[bmi_category]))
    height_cm = float(rng.normal(153.4, 6.2))
    height_m = height_cm / 100
    weight_kg = round(bmi * height_m ** 2, 1)
    bmi = round(bmi, 1)

    # Haemoglobin
    base_anaemia_prob = 0.478 + anaemia_adj
    is_anaemic = rng.random() < clamp(base_anaemia_prob, 0.0, 1.0)
    if is_anaemic:
        severity = rng.choice(["mild", "moderate", "severe"], p=[0.548, 0.410, 0.042])
        hb_ranges = {"mild": (10.0, 11.9), "moderate": (7.0, 9.9), "severe": (3.5, 6.9)}
        hb = round(float(rng.uniform(*hb_ranges[severity])), 1)
    else:
        hb = round(float(rng.normal(12.8, 1.4)), 1)
        hb = clamp(hb, 11.0, 17.0)

    # Blood pressure
    is_hypertensive = rng.random() < 0.105
    if is_hypertensive:
        sbp = int(rng.normal(152.3, 18.4))
        dbp = int(rng.normal(96.4, 11.2))
    else:
        sbp = int(rng.normal(112.4, 14.2))
        dbp = int(rng.normal(72.8, 9.6))
    sbp = clamp(sbp, 80, 200)
    dbp = clamp(dbp, 50, 130)

    # Blood glucose
    is_diabetic = rng.random() < 0.098
    if is_diabetic:
        fasting_glucose = round(float(rng.normal(162.8, 42.6)), 1)
    else:
        fasting_glucose = round(float(rng.normal(88.4, 10.2)), 1)
    fasting_glucose = clamp(fasting_glucose, 50.0, 400.0)

    # Pregnancy / ANC
    lmp_date = None
    anc_visits = 0
    if is_pregnant:
        lmp_date = date.today() - timedelta(days=int(rng.integers(28, 280)))
        anc_category = rng.choice(
            ["none", "1_to_3", "4_plus"],
            p=[0.031, 0.241, 0.728]
        )
        anc_visits = {"none": 0, "1_to_3": int(rng.integers(1, 4)), "4_plus": int(rng.integers(4, 9))}[anc_category]

    # Immunization (for women with children; proxy for child record)
    fully_immunized = rng.random() < 0.652
    vacc_status = "complete" if fully_immunized else rng.choice(["partial", "none"], p=[0.84, 0.16])

    # Registration
    reg_date = random_date(date(2020, 1, 1), date.today() - timedelta(days=30))
    last_visit = random_date(reg_date, date.today())

    return {
        "patient_id":       patient_id,
        "district":         district,
        "age":              age,
        "dob":              dob.isoformat(),
        "height_cm":        round(height_cm, 1),
        "weight_kg":        weight_kg,
        "bmi":              bmi,
        "bmi_category":     bmi_category,
        "hemoglobin":       hb,
        "is_anaemic":       is_anaemic,
        "sbp":              sbp,
        "dbp":              dbp,
        "is_hypertensive":  is_hypertensive,
        "fasting_glucose":  fasting_glucose,
        "is_diabetic":      is_diabetic,
        "is_pregnant":      is_pregnant,
        "lmp_date":         lmp_date.isoformat() if lmp_date else None,
        "anc_visits":       anc_visits,
        "vacc_status":      vacc_status,
        "registration_date": reg_date.isoformat(),
        "last_visit_date":  last_visit.isoformat(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Multi-source record generator (add measurement noise per source)
# ──────────────────────────────────────────────────────────────────────────────

def measurement_noise(value, noise_std: float, lo=None, hi=None):
    noisy = value + rng.normal(0, noise_std)
    if lo is not None and hi is not None:
        noisy = clamp(noisy, lo, hi)
    return round(float(noisy), 1)


def generate_source_record(gt: dict, source: str, record_id: str) -> dict:
    """Create a single source's version of the patient record (with noise)."""
    reliability = SOURCE_RELIABILITY[source]
    noise_scale = 1.0 + (1.0 - reliability) * 3.0  # low-reliability = more noise

    entry_lag_mean, entry_lag_std = DATA_ENTRY_DELAY[source]
    entry_lag_days = max(0, int(rng.normal(entry_lag_mean, entry_lag_std)))
    entry_date = (date.today() - timedelta(days=entry_lag_days)).isoformat()

    # Height / weight / BMI (with calibration noise)
    height = measurement_noise(gt["height_cm"], 0.8 * noise_scale, 130, 190)
    weight = measurement_noise(gt["weight_kg"], 0.5 * noise_scale, 25, 120)
    bmi_calc = round(weight / ((height / 100) ** 2), 1)

    # Haemoglobin
    hb = measurement_noise(gt["hemoglobin"], 0.4 * noise_scale, 3.0, 18.0)

    # BP
    sbp = int(measurement_noise(gt["sbp"], 5 * noise_scale, 70, 220))
    dbp = int(measurement_noise(gt["dbp"], 3 * noise_scale, 40, 140))

    # Glucose
    glucose = measurement_noise(gt["fasting_glucose"], 5 * noise_scale, 45, 450)

    # Age (slight transcription error possible)
    age = gt["age"] if rng.random() < reliability else gt["age"] + rng.choice([-1, 0, 1])

    # Pregnancy status (categorical — AWW/ASHA may lag behind clinical)
    if source in ["aww", "asha"] and gt["is_pregnant"]:
        pregnancy_recorded = rng.random() < 0.85
    else:
        pregnancy_recorded = gt["is_pregnant"]

    # Vaccination
    vacc = gt["vacc_status"]
    if rng.random() > reliability:
        vacc = rng.choice(["complete", "partial", "none"])

    return {
        "record_id":        record_id,
        "patient_id":       gt["patient_id"],
        "source":           source,
        "entry_date":       entry_date,
        "district":         gt["district"],
        "age_recorded":     age,
        "height_cm":        height,
        "weight_kg":        weight,
        "bmi":              bmi_calc,
        "hemoglobin":       hb,
        "sbp":              sbp,
        "dbp":              dbp,
        "fasting_glucose":  glucose,
        "is_pregnant":      pregnancy_recorded,
        "anc_visits":       gt["anc_visits"],
        "vacc_status":      vacc,
        "registration_date": gt["registration_date"],
        "last_visit_date":  gt["last_visit_date"],
        "source_reliability": reliability,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Conflict injector
# ──────────────────────────────────────────────────────────────────────────────

def inject_conflict(record: dict, gt: dict, conflict_type: str) -> dict:
    """Mutate a record to introduce a specific conflict type."""
    r = record.copy()

    if conflict_type == "numeric_outlier":
        field = rng.choice(["hemoglobin", "weight_kg", "sbp", "fasting_glucose"])
        if field == "hemoglobin":
            r["hemoglobin"] = round(float(rng.choice([
                rng.uniform(1.5, 3.4),     # impossibly low
                rng.uniform(20.0, 25.0),   # impossibly high
            ])), 1)
        elif field == "weight_kg":
            r["weight_kg"] = round(float(rng.uniform(200, 250)), 1)
        elif field == "sbp":
            r["sbp"] = int(rng.uniform(230, 280))
        elif field == "fasting_glucose":
            r["fasting_glucose"] = round(float(rng.uniform(500, 700)), 1)

    elif conflict_type == "categorical_mismatch":
        r["vacc_status"] = rng.choice(
            [v for v in ["complete", "partial", "none"] if v != gt["vacc_status"]]
        )

    elif conflict_type == "temporal_inconsistency":
        # Entry date before registration date
        reg = date.fromisoformat(gt["registration_date"])
        r["entry_date"] = (reg - timedelta(days=int(rng.integers(1, 90)))).isoformat()

    elif conflict_type == "demographic_drift":
        r["age_recorded"] = gt["age"] + int(rng.choice([-5, -4, 4, 5, 6, 7]))

    elif conflict_type == "physiological_impossibility":
        # Haemoglobin < 5 without any clinical flag
        r["hemoglobin"] = round(float(rng.uniform(1.0, 4.9)), 1)
        r["is_pregnant"] = False

    elif conflict_type == "cross_field_contradiction":
        # Pregnant=No but LMP date recorded this month
        r["is_pregnant"] = False
        r["anc_visits"] = 0

    r["has_conflict"] = True
    r["conflict_type"] = conflict_type
    return r


# ──────────────────────────────────────────────────────────────────────────────
# Main generation pipeline
# ──────────────────────────────────────────────────────────────────────────────

def generate_dataset(n_patients: int, output_dir: str, seed: int = None):
    if seed is not None:
        set_seed(seed)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ground_truths = []
    all_source_records = []

    conflict_types = list(CONFLICT_TYPE_WEIGHTS.keys())
    conflict_weights = list(CONFLICT_TYPE_WEIGHTS.values())

    print(f"[1/4] Generating {n_patients} patient ground truths...")
    for i in range(n_patients):
        pid = f"KA-{str(uuid.uuid4())[:8].upper()}"
        district = sample_district()
        gt = generate_ground_truth(pid, district)
        ground_truths.append(gt)

        # ── Generate source records (2–6 sources per patient) ──────────────
        n_sources = int(rng.integers(2, 7))
        chosen_sources = random.sample(SOURCES, n_sources)

        patient_records = []
        for src in chosen_sources:
            rid = f"REC-{str(uuid.uuid4())[:8].upper()}"
            rec = generate_source_record(gt, src, rid)
            rec["has_conflict"] = False
            rec["conflict_type"] = None
            patient_records.append(rec)

        # ── Inject conflicts ───────────────────────────────────────────────
        if rng.random() < 0.231:  # NFHS-5 estimated discordance rate
            n_conflicts = int(rng.integers(1, min(3, len(patient_records)) + 1))
            conflict_indices = random.sample(range(len(patient_records)), n_conflicts)
            for ci in conflict_indices:
                ct = rng.choice(conflict_types, p=conflict_weights)
                patient_records[ci] = inject_conflict(patient_records[ci], gt, ct)

        all_source_records.extend(patient_records)

        if (i + 1) % 5000 == 0:
            print(f"  ✓ {i+1}/{n_patients} patients generated")

    print("[2/4] Building DataFrames...")
    df_gt = pd.DataFrame(ground_truths)
    df_records = pd.DataFrame(all_source_records)

    # ── Conflict summary ──────────────────────────────────────────────────────
    total_records = len(df_records)
    conflicted = df_records["has_conflict"].sum()
    conflict_rate = conflicted / total_records

    print("[3/4] Writing output files...")
    df_gt.to_csv(os.path.join(output_dir, "ground_truth.csv"), index=False)
    df_records.to_csv(os.path.join(output_dir, "source_records.csv"), index=False)

    # Conflict-only subset
    df_records[df_records["has_conflict"]].to_csv(
        os.path.join(output_dir, "conflicts_only.csv"), index=False
    )

    # ── Dataset metadata ──────────────────────────────────────────────────────
    meta = {
        "generated_at":     datetime.now().isoformat(),
        "n_patients":       n_patients,
        "total_records":    total_records,
        "conflicted_records": int(conflicted),
        "conflict_rate":    round(float(conflict_rate), 4),
        "seed":             seed,
        "source_distribution": df_records["source"].value_counts().to_dict(),
        "conflict_type_distribution": df_records[df_records["has_conflict"]]["conflict_type"].value_counts().to_dict(),
        "district_distribution": df_records["district"].value_counts().to_dict(),
        "nfhs5_reference":  "Karnataka State Fact Sheet, NFHS-5 (2019-21)",
    }
    with open(os.path.join(output_dir, "dataset_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("[4/4] Done!")
    print(f"\n{'='*55}")
    print(f"  Dataset Summary")
    print(f"{'='*55}")
    print(f"  Patients generated   : {n_patients:,}")
    print(f"  Total source records : {total_records:,}")
    print(f"  Conflicted records   : {int(conflicted):,} ({conflict_rate:.1%})")
    print(f"  Output directory     : {output_dir}")
    print(f"{'='*55}\n")

    print("  Conflict types:")
    for ct, cnt in meta["conflict_type_distribution"].items():
        print(f"    {ct:<35} {cnt:>6,}")

    print("\n  Source distribution:")
    for src, cnt in meta["source_distribution"].items():
        print(f"    {src:<25} {cnt:>8,} records")

    return df_gt, df_records


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic NFHS-5 Karnataka health records with conflicts"
    )
    parser.add_argument("--n_patients", type=int, default=10000,
                        help="Number of patients to generate (default: 10000)")
    parser.add_argument("--output", type=str, default="data/synthetic/",
                        help="Output directory (default: data/synthetic/)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    generate_dataset(
        n_patients=args.n_patients,
        output_dir=args.output,
        seed=args.seed,
    )
