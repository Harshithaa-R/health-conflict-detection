import pandas as pd
import numpy as np
import os
from rapidfuzz import fuzz


# ---------------------------------------------------
# TRANSLITERATION VARIANTS
# Mirrors the logic in generate_maternal_dataset.py
# so we normalise names before comparing
# ---------------------------------------------------

TRANSLITERATION_MAP = {
    "savita":   "savitha",
    "laxmi":    "lakshmi",
    "crishna":  "krishna",
    "radhamma": "radha",
    "gita":     "geetha",
    "swetha":   "shwetha",
    "kavita":   "kavitha",
    "sooma":    "suma",
    "rekamma":  "rekha",
    "pushpamma":"pushpa",
    "manjamma": "manjula",
    "sunita":   "sunitha",
    "anita":    "anitha",
    "nirmamma": "nirmala",
    "shanta":   "shantha",
}


def normalise_name(name: str) -> str:
    name = str(name).strip().lower()
    for variant, canonical in TRANSLITERATION_MAP.items():
        name = name.replace(variant, canonical)
    return name


# ---------------------------------------------------
# THRESHOLDS
# ---------------------------------------------------

NAME_SIMILARITY_THRESHOLD = 85   # below = conflict
AGE_DIFF_THRESHOLD         = 3   # years


def detect_identity_conflicts():

    print("Loading linked records...")

    df = pd.read_csv(
        "data/processed/linked_records.csv",
        low_memory=False
    )

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    conflicts = []

    total_name   = 0
    total_age    = 0
    total_gender = 0
    multi_cases  = 0

    grouped = df.groupby("unified_patient_id")

    for uid, group in grouped:

        patient_conflicts = []

        # ---------------------------------------------------
        # NAME CONFLICT
        # ---------------------------------------------------

        names = (
            group["name"]
            .dropna()
            .apply(normalise_name)
            .tolist()
        )

        if len(names) > 1:

            min_sim = 100

            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    score = fuzz.token_sort_ratio(
                        names[i], names[j]
                    )
                    if score < min_sim:
                        min_sim = score

            if min_sim < NAME_SIMILARITY_THRESHOLD:
                patient_conflicts.append("name_conflict")
                total_name += 1

        # ---------------------------------------------------
        # AGE CONFLICT
        # ---------------------------------------------------

        ages = group["age"].dropna().tolist()

        if len(ages) > 1:
            if max(ages) - min(ages) > AGE_DIFF_THRESHOLD:
                patient_conflicts.append("age_conflict")
                total_age += 1

        # ---------------------------------------------------
        # GENDER CONFLICT
        # ---------------------------------------------------

        if "gender" in group.columns:
            genders = (
                group["gender"]
                .dropna()
                .str.strip()
                .str.upper()
                .unique()
                .tolist()
            )
            if len(genders) > 1:
                patient_conflicts.append("gender_conflict")
                total_gender += 1

        if len(patient_conflicts) > 1:
            multi_cases += 1

        conflicts.append({
            "unified_patient_id":    uid,
            "patient_id":            group.iloc[0]["patient_id"],
            "domain":                group.iloc[0].get("domain", "maternal"),
            "name":                  group.iloc[0]["name"],
            "district":              group.iloc[0]["district"],
            "village":               group.iloc[0]["village"],
            "num_identity_conflicts": len(patient_conflicts),
            "identity_conflict_types": (
                ",".join(patient_conflicts)
                if patient_conflicts else "no_identity_conflict"
            ),
            "has_identity_conflict": len(patient_conflicts) > 0,
        })

    conflicts_df = pd.DataFrame(conflicts)

    os.makedirs("data/processed", exist_ok=True)

    conflicts_df.to_csv(
        "data/processed/identity_conflicts.csv",
        index=False
    )

    print("\nIdentity Conflict Summary")
    print("=" * 50)

    total     = len(conflicts_df)
    with_conf = int(conflicts_df["has_identity_conflict"].sum())

    print(f"Patients Analysed       : {total:,}")
    print(f"With Identity Conflicts : {with_conf:,}  ({with_conf/total*100:.1f}%)")
    print(f"  Name Conflicts        : {total_name:,}")
    print(f"  Age Conflicts         : {total_age:,}")
    print(f"  Gender Conflicts      : {total_gender:,}")
    print(f"Multi-type conflicts    : {multi_cases:,}")

    print("\nBy Domain:")
    for domain in ["maternal", "child", "chronic"]:
        d = conflicts_df[conflicts_df["domain"] == domain]
        wc = int(d["has_identity_conflict"].sum())
        if len(d) > 0:
            print(f"  {domain:<10}: {wc:,} / {len(d):,} ({wc/len(d)*100:.1f}%)")

    print("\nSaved: data/processed/identity_conflicts.csv")

    return conflicts_df


if __name__ == "__main__":

    detect_identity_conflicts()