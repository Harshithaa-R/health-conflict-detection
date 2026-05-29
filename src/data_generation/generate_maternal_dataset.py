# src/data_generation/generate_maternal_dataset.py

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker('en_IN')

np.random.seed(42)
random.seed(42)

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

NUM_PATIENTS = 5000

LOCATIONS = [

    ("Tumkur", "Eeramaranahalli", "Sira"),
    ("Tumkur", "Kora", "Gubbi"),
    ("Tumkur", "Handanakere", "Turuvekere"),

    ("Mysore", "Nanjangud", "Nanjangud"),
    ("Mysore", "Hunsur", "Hunsur"),
    ("Mysore", "Saligrama", "K R Nagar"),

    ("Mandya", "Maddur", "Maddur"),
    ("Mandya", "Malavalli", "Malavalli"),
    ("Mandya", "Nagamangala", "Nagamangala"),

    ("Kolar", "Mulbagal", "Mulbagal"),
    ("Kolar", "Bangarpet", "Bangarpet"),
    ("Kolar", "Malur", "Malur"),

    ("Hassan", "Arsikere", "Arsikere"),
    ("Hassan", "Belur", "Belur"),
    ("Hassan", "Sakleshpur", "Sakleshpur"),

    ("Davanagere", "Harihar", "Harihar"),
    ("Davanagere", "Honnali", "Honnali"),
    ("Davanagere", "Jagalur", "Jagalur"),

    ("Chikkaballapur", "Bagepalli", "Bagepalli"),
    ("Chikkaballapur", "Sidlaghatta", "Sidlaghatta"),
    ("Chikkaballapur", "Gudibande", "Gudibande"),

    ("Kalaburagi", "Chincholi", "Chincholi"),
    ("Kalaburagi", "Sedam", "Sedam"),
    ("Kalaburagi", "Jewargi", "Jewargi"),

    ("Shivamogga", "Bhadravati", "Bhadravati"),
    ("Shivamogga", "Sagar", "Sagar"),
    ("Shivamogga", "Shikaripura", "Shikaripura"),

    ("Belagavi", "Gokak", "Gokak"),
    ("Belagavi", "Athani", "Athani"),
    ("Belagavi", "Ramdurg", "Ramdurg")
]

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------

def random_date(start_days=0, end_days=250):

    today = datetime.today()

    delta = random.randint(start_days, end_days)

    return (
        today - timedelta(days=delta)
    ).strftime('%d-%m-%Y')


def calculate_edd(lmp_date):

    lmp = datetime.strptime(lmp_date, '%d-%m-%Y')

    edd = lmp + timedelta(days=280)

    return edd.strftime('%d-%m-%Y')


def transliterate_name(name):

    variations = {
        "Savitha": "Savita",
        "Lakshmi": "Laxmi",
        "Krishna": "Crishna",
        "Radha": "Radhamma",
        "Geetha": "Gita",
        "Shwetha": "Swetha",
        "Kavitha": "Kavita"
    }

    first = name.split()[0]

    if first in variations:
        return name.replace(first, variations[first])

    return name


# ---------------------------------------------------
# GENERATE BASE PATIENTS
# ---------------------------------------------------

patients = []

for i in range(1, NUM_PATIENTS + 1):

    patient_id = f"W{i:05d}"


    district, village, taluk = random.choice(LOCATIONS)

    name = fake.name_female()

    age = random.randint(19, 38)

    dob = (
        datetime.today() - timedelta(days=age * 365)
    ).strftime('%d-%m-%Y')

    gravida = random.randint(1, 4)

    parity = max(0, gravida - 1)

    gestational_age = random.randint(8, 38)

    lmp = (
        datetime.today() - timedelta(days=gestational_age * 7)
    ).strftime('%d-%m-%Y')

    edd = calculate_edd(lmp)

    systolic_bp = int(np.random.normal(118, 12))
    systolic_bp = max(90, min(170, systolic_bp))

    diastolic_bp = int(np.random.normal(76, 8))
    diastolic_bp = max(50, min(120, diastolic_bp))

    hb = round(np.random.normal(10.8, 1.3), 1)
    hb = max(6.5, min(14.5, hb))

    weight = round(np.random.normal(58, 10), 1)
    weight = max(40, min(95, weight))

    anc_visits = np.random.choice(
        [1, 2, 3, 4, 5, 6],
        p=[0.05, 0.10, 0.20, 0.35, 0.20, 0.10]
    )

    fundal_height = round(np.random.normal(28, 5), 1)
    fundal_height = max(12, min(40, fundal_height))

    blood_sugar = round(np.random.normal(95, 20), 1)
    blood_sugar = max(65, min(220, blood_sugar))

    urine_albumin = np.random.choice(
        ["negative", "trace", "positive"],
        p=[0.75, 0.20, 0.05]
    )

    oedema = np.random.choice(
        [0, 1],
        p=[0.90, 0.10]
    )

    pallor = 1 if hb < 9 else 0

    # ---------------------------------------------------
    # HIGH RISK LOGIC
    # ---------------------------------------------------

    high_risk = 0

    risk_reasons = []

    if hb < 9:
        high_risk = 1
        risk_reasons.append("severe_anaemia")

    if systolic_bp > 140:
        high_risk = 1
        risk_reasons.append("hypertension")

    if blood_sugar > 140:
        high_risk = 1
        risk_reasons.append("gestational_diabetes")

    if gestational_age > 34 and anc_visits < 2:
        high_risk = 1
        risk_reasons.append("missed_anc")

    patients.append({

        'patient_id': patient_id,
        'patient_type': 'woman',

        'name': name,
        'age': age,
        'dob': dob,

        'gender': 'F',

        'village': village,
        'district': district,
        'taluk': taluk,

        'pregnancy_status': 'pregnant',

        'gravida': gravida,
        'parity': parity,

        'lmp_date': lmp,
        'edd': edd,

        'gestational_age_weeks': gestational_age,

        'anc_visits_count': anc_visits,

        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,

        'weight_kg': weight,

        'haemoglobin_gdl': hb,

        'urine_albumin': urine_albumin,

        'oedema_present': oedema,
        'pallor_present': pallor,

        'blood_sugar_fasting': blood_sugar,

        'fundal_height_cm': fundal_height,

        'tt_1_given': random.choice([0, 1]),
        'tt_2_given': random.choice([0, 1]),

        'ifa_tablets_given': random.randint(30, 180),

        'visit_date': random_date(0, 180),
        'record_entry_date': random_date(0, 200),
        'source_record_id': None,
        'unified_patient_id': None,
        'conflict_type': 'no_conflict',
        'conflict_field': '',
        'severity_score': 0,
        'true_high_risk': high_risk,

        'true_high_risk_reason': (
            ",".join(risk_reasons)
            if risk_reasons else "none"
        )
    })

# ---------------------------------------------------
# GENERATE MULTI-SOURCE RECORDS
# ---------------------------------------------------

records = []

for p in patients:

    # =================================================
    # ASHA
    # =================================================

    asha = p.copy()

    asha['cadre'] = 'ASHA'
    asha['data_source'] = 'ASHA'
    asha['source_record_id'] = f"ASHA_{p['patient_id']}"
    if random.random() < 0.30:
        asha['age'] += random.choice([-1, 1])

    if random.random() < 0.35:
        asha['haemoglobin_gdl'] += round(
            random.uniform(-1.0, 1.0), 1
        )

    if random.random() < 0.30:
        asha['systolic_bp'] += random.randint(-20, 20)

    if random.random() < 0.25:
        asha['anc_visits_count'] += random.choice([-1, 1])

    if random.random() < 0.30:
        asha['blood_sugar_fasting'] += round(
            random.uniform(-35, 35), 1
        )

    if random.random() < 0.20:
        asha['weight_kg'] += round(
            random.uniform(-4, 4), 1
        )

    if random.random() < 0.20:
        asha['fundal_height_cm'] += round(
            random.uniform(-3, 3), 1
        )

    if random.random() < 0.40:
        asha['name'] = transliterate_name(
            asha['name']
        )

    records.append(asha)

    # =================================================
    # ANM
    # =================================================

    anm = p.copy()

    anm['cadre'] = 'ANM'
    anm['data_source'] = 'ANM'
    anm['source_record_id'] = f"ANM_{p['patient_id']}"
    if random.random() < 0.05:
        anm['haemoglobin_gdl'] += round(
            random.uniform(-0.3, 0.3), 1
        )

    if random.random() < 0.05:
        anm['systolic_bp'] += random.randint(-3, 3)

    if random.random() < 0.05:
        anm['blood_sugar_fasting'] += round(
            random.uniform(-8, 8), 1
        )

    records.append(anm)

    # =================================================
    # PHC
    # =================================================

    phc = p.copy()

    phc['cadre'] = 'PHC'
    phc['data_source'] = 'PHC'
    phc['source_record_id'] = f"PHC_{p['patient_id']}"
    if random.random() < 0.02:
        phc['haemoglobin_gdl'] += round(
            random.uniform(-0.1, 0.1), 1
        )

    if random.random() < 0.02:
        phc['systolic_bp'] += random.randint(-2, 2)

    if random.random() < 0.02:
        phc['blood_sugar_fasting'] += round(
            random.uniform(-3, 3), 1
        )

    records.append(phc)

    # =================================================
    # ANGANWADI
    # =================================================

    ang = p.copy()

    ang['cadre'] = 'ANGANWADI'
    ang['data_source'] = 'ANGANWADI'
    ang['source_record_id'] = f"ANG_{p['patient_id']}"
    if random.random() < 0.15:
        ang['weight_kg'] += round(
            random.uniform(-3, 3), 1
        )

    if random.random() < 0.20:
        ang['ifa_tablets_given'] += random.randint(
            -20,
            20
        )

    if random.random() < 0.20:
        ang['anc_visits_count'] += random.choice(
            [-1, 1]
        )

    if random.random() < 0.15:
        ang['blood_sugar_fasting'] += round(
            random.uniform(-20, 20), 1
        )

    records.append(ang)

df = pd.DataFrame(records)
# ---------------------------------------------------
# SAVE DATASETS
# ---------------------------------------------------

os.makedirs('data/synthetic', exist_ok=True)

asha_df = df[df['cadre'] == 'ASHA']
anm_df = df[df['cadre'] == 'ANM']
phc_df = df[df['cadre'] == 'PHC']
anganwadi_df = df[df['cadre'] == 'ANGANWADI']

asha_df.to_csv(
    'data/synthetic/asha_maternal.csv',
    index=False
)

anm_df.to_csv(
    'data/synthetic/anm_maternal.csv',
    index=False
)

phc_df.to_csv(
    'data/synthetic/phc_maternal.csv',
    index=False
)

anganwadi_df.to_csv(
    'data/synthetic/anganwadi_maternal.csv',
    index=False
)

df.to_csv(
    'data/synthetic/maternal_records.csv',
    index=False
)


print("\nDataset Generated Successfully")
print("=" * 60)

print(f"Total Patients       : {NUM_PATIENTS:,}")
print(f"Total Records        : {len(df):,}")

print("\nCadre Distribution")
print(df['cadre'].value_counts())

print("\nHigh Risk Cases")
print(df['true_high_risk'].value_counts())

print("\nAverage Hb")
print(round(df['haemoglobin_gdl'].mean(), 2))

print("\nAverage Systolic BP")
print(round(df['systolic_bp'].mean(), 2))

print("\nAverage Blood Sugar")
print(round(df['blood_sugar_fasting'].mean(), 2))

print("\nUnique Patients")
print(df['patient_id'].nunique())

print("\nFiles Generated")
print("- data/synthetic/asha_maternal.csv")
print("- data/synthetic/anm_maternal.csv")
print("- data/synthetic/phc_maternal.csv")
print("- data/synthetic/anganwadi_maternal.csv")
print("- data/synthetic/maternal_records.csv")