import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta


# ---------------------------------------------------
# THRESHOLDS
# ---------------------------------------------------

VISIT_DATE_GAP_DAYS = 30
EDD_GAP_DAYS        = 14
LMP_GAP_DAYS        = 14
STALE_RECORD_DAYS   = 180
MAX_GA_WEEKS        = 42
MIN_GA_WEEKS        = 4


def safe_parse_date(val):
    if pd.isna(val):
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except ValueError:
            continue
    return None


def date_gap_days(dates: list) -> float:
    parsed = [safe_parse_date(d) for d in dates]
    parsed = [d for d in parsed if d is not None]
    if len(parsed) < 2:
        return 0.0
    return (max(parsed) - min(parsed)).days


def detect_temporal_conflicts():

    print("Loading unified health records...")

    # Read from unified synthetic records — has all date fields
    unified_path = "data/synthetic/unified_health_records.csv"
    fallback_path = "data/synthetic/maternal_records.csv"

    if os.path.exists(unified_path):
        df = pd.read_csv(unified_path, low_memory=False)
    else:
        print("Falling back to maternal_records.csv...")
        df = pd.read_csv(fallback_path, low_memory=False)
        df["domain"] = "maternal"

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    conflicts = []

    total_visit   = 0
    total_edd     = 0
    total_lmp     = 0
    total_stale   = 0
    total_ga      = 0
    multi_cases   = 0

    today = datetime.today()

    grouped = df.groupby("patient_id")

    for pid, group in grouped:

        domain = group.iloc[0].get("domain", "maternal")
        patient_conflicts = []

        # ---------------------------------------------------
        # VISIT DATE CONFLICT — all domains
        # ---------------------------------------------------

        if "visit_date" in group.columns:
            gap = date_gap_days(group["visit_date"].dropna().tolist())
            if gap > VISIT_DATE_GAP_DAYS:
                patient_conflicts.append("visit_date_conflict")
                total_visit += 1

        # ---------------------------------------------------
        # STALE RECORD — all domains
        # ---------------------------------------------------

        if "record_entry_date" in group.columns:
            parsed = [
                safe_parse_date(d)
                for d in group["record_entry_date"].dropna().tolist()
            ]
            parsed = [d for d in parsed if d is not None]
            if parsed:
                days_since = (today - max(parsed)).days
                if days_since > STALE_RECORD_DAYS:
                    patient_conflicts.append("stale_record_conflict")
                    total_stale += 1

        # ---------------------------------------------------
        # MATERNAL-SPECIFIC DATE CONFLICTS
        # ---------------------------------------------------

        if domain == "maternal":

            if "edd" in group.columns:
                gap = date_gap_days(group["edd"].dropna().tolist())
                if gap > EDD_GAP_DAYS:
                    patient_conflicts.append("edd_conflict")
                    total_edd += 1

            if "lmp_date" in group.columns:
                gap = date_gap_days(group["lmp_date"].dropna().tolist())
                if gap > LMP_GAP_DAYS:
                    patient_conflicts.append("lmp_conflict")
                    total_lmp += 1

            if "gestational_age_weeks" in group.columns:
                ga_vals = group["gestational_age_weeks"].dropna().tolist()
                implausible = any(
                    v < MIN_GA_WEEKS or v > MAX_GA_WEEKS
                    for v in ga_vals
                )
                inter_gap = (
                    max(ga_vals) - min(ga_vals) > 4
                    if len(ga_vals) > 1 else False
                )
                if implausible or inter_gap:
                    patient_conflicts.append("gestational_age_conflict")
                    total_ga += 1

        if len(patient_conflicts) > 1:
            multi_cases += 1

        conflicts.append({
            "patient_id":              pid,
            "domain":                  domain,
            "name":                    group.iloc[0]["name"],
            "district":                group.iloc[0]["district"],
            "village":                 group.iloc[0]["village"],
            "num_temporal_conflicts":  len(patient_conflicts),
            "temporal_conflict_types": (
                ",".join(patient_conflicts)
                if patient_conflicts else "no_temporal_conflict"
            ),
            "has_temporal_conflict":   len(patient_conflicts) > 0,
        })

    conflicts_df = pd.DataFrame(conflicts)

    os.makedirs("data/processed", exist_ok=True)

    conflicts_df.to_csv(
        "data/processed/temporal_conflicts.csv",
        index=False
    )

    print("\nTemporal Conflict Summary")
    print("=" * 50)

    total     = len(conflicts_df)
    with_conf = int(conflicts_df["has_temporal_conflict"].sum())

    print(f"Patients Analysed         : {total:,}")
    print(f"With Temporal Conflicts   : {with_conf:,}  ({with_conf/total*100:.1f}%)")
    print(f"  Visit Date Conflicts    : {total_visit:,}")
    print(f"  EDD Conflicts           : {total_edd:,}")
    print(f"  LMP Conflicts           : {total_lmp:,}")
    print(f"  Stale Record Conflicts  : {total_stale:,}")
    print(f"  Gestational Age Conflicts: {total_ga:,}")
    print(f"Multi-type conflicts      : {multi_cases:,}")

    print("\nBy Domain:")
    for domain in ["maternal", "child", "chronic"]:
        d = conflicts_df[conflicts_df["domain"] == domain]
        wc = int(d["has_temporal_conflict"].sum())
        if len(d) > 0:
            print(f"  {domain:<10}: {wc:,} / {len(d):,} ({wc/len(d)*100:.1f}%)")

    print("\nSaved: data/processed/temporal_conflicts.csv")

    return conflicts_df


if __name__ == "__main__":

    detect_temporal_conflicts()