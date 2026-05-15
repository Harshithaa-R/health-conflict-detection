import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

# ── NFHS-5 Karnataka Reference Distributions ──────────────────────────────────

DISTRICTS = [
    'Bengaluru Urban', 'Bengaluru Rural', 'Mysuru', 'Tumkur',
    'Belagavi', 'Dharwad', 'Dakshina Kannada', 'Shivamogga',
    'Kalaburagi', 'Ballari', 'Raichur', 'Hassan',
    'Mandya', 'Chikkamagaluru', 'Uttara Kannada'
]

TALUKS = {
    'Bengaluru Urban': ['Bengaluru North', 'Bengaluru South', 'Yelahanka'],
    'Mysuru': ['Mysuru', 'Hunsur', 'Nanjangud'],
    'Tumkur': ['Tumkur', 'Tiptur', 'Madhugiri'],
    'Belagavi': ['Belagavi', 'Gokak', 'Chikkodi'],
    'Dharwad': ['Dharwad', 'Hubli', 'Kalghatgi'],
    'Dakshina Kannada': ['Mangaluru', 'Puttur', 'Bantwal'],
    'Shivamogga': ['Shivamogga', 'Sagar', 'Bhadravati'],
    'Kalaburagi': ['Kalaburagi', 'Afzalpur', 'Chincholi'],
    'Ballari': ['Ballari', 'Sandur', 'Hospet'],
    'Raichur': ['Raichur', 'Sindhanur', 'Manvi'],
    'Hassan': ['Hassan', 'Belur', 'Sakleshpur'],
    'Mandya': ['Mandya', 'Maddur', 'Nagamangala'],
    'Chikkamagaluru': ['Chikkamagaluru', 'Kadur', 'Mudigere'],
    'Uttara Kannada': ['Karwar', 'Sirsi', 'Kumta'],
    'Bengaluru Rural': ['Doddaballapur', 'Hosakote', 'Nelamangala']
}

VILLAGES = [
    'Arasikere', 'Belakavadi', 'Channapatna', 'Dodderi',
    'Eeramaranahalli', 'Gowdanahalli', 'Hosakere', 'Iggalur',
    'Jakkanahalli', 'Kaggalipura', 'Lakkavalli', 'Maranahalli',
    'Nallur', 'Oordigere', 'Palahalli', 'Ramanahalli',
    'Siddapura', 'Tavarekere', 'Ukkadagatri', 'Vaderahalli'
]

# Kannada female names with transliteration variants
KANNADA_NAMES = {
    'Lakshmi':      ['Lakshmi',    'Laxmi',       'Lakshme',     'L.'],
    'Kaveri':       ['Kaveri',     'Cauvery',      'Kavery',      'K.'],
    'Savitha':      ['Savitha',    'Savita',       'Savitha',     'S.'],
    'Radha':        ['Radha',      'Radhamma',     'Radha',       'R.'],
    'Meena':        ['Meena',      'Mina',         'Meenakshi',   'M.'],
    'Suma':         ['Suma',       'Suman',        'Sumathi',     'S.'],
    'Geetha':       ['Geetha',     'Gita',         'Geeta',       'G.'],
    'Anitha':       ['Anitha',     'Anita',        'Anitha',      'A.'],
    'Pushpa':       ['Pushpa',     'Pushpamma',    'Pushpa',      'P.'],
    'Vani':         ['Vani',       'Vaani',        'Vani',        'V.'],
    'Sharada':      ['Sharada',    'Sharda',       'Sharadha',    'S.'],
    'Usha':         ['Usha',       'Usha',         'Ushadevi',    'U.'],
    'Rekha':        ['Rekha',      'Rekha',        'Rekhamma',    'R.'],
    'Krishnamma':   ['Krishnamma', 'Krishnama',    'Krishnaveni', 'K.'],
    'Bhagyamma':    ['Bhagyamma',  'Bhagya',       'Bhagyavathi', 'B.'],
    'Nagamma':      ['Nagamma',    'Naga',         'Nagaveni',    'N.'],
    'Yellamma':     ['Yellamma',   'Yellama',      'Yallamma',    'Y.'],
    'Parvathi':     ['Parvathi',   'Parvati',      'Paarvathi',   'P.'],
    'Girija':       ['Girija',     'Girisha',      'Girijamma',   'G.'],
    'Kamala':       ['Kamala',     'Kamala',       'Kamalamma',   'K.']
}

KANNADA_SURNAMES = [
    'Gowda', 'Naik', 'Reddy', 'Rao', 'Hegde',
    'Nayak', 'Patil', 'Shetty', 'Kumar', 'Swamy',
    'Naidu', 'Murthy', 'Raju', 'Sharma', 'Verma',
    'Lingaiah', 'Basavaiah', 'Hanumaiah', 'Venkatesha', 'Siddaraju'
]

CASTE_CATEGORIES = ['SC', 'ST', 'OBC', 'General']
CASTE_PROBS = [0.18, 0.07, 0.44, 0.31]  # Karnataka approximate proportions

CADRES = ['ASHA', 'ANM', 'PHC', 'Anganwadi']

# Fields each cadre is RESPONSIBLE for recording
# Only these fields can have missing-in-source conflicts
CADRE_RESPONSIBLE_FIELDS = {
    'ASHA': [
        'name', 'age', 'dob', 'systolic_bp', 'diastolic_bp',
        'weight_kg', 'anc_visits_count', 'lmp_date', 'edd',
        'pregnancy_status', 'tt_1_given', 'tt_2_given',
        'ifa_tablets_given', 'delivery_place', 'institutional_delivery',
        'full_immunisation_status', 'child_weight_kg',
        'vaccinated', 'oedema_present', 'pallor_present'
    ],
    'ANM': [
        'name', 'age', 'dob', 'systolic_bp', 'diastolic_bp',
        'weight_kg', 'haemoglobin_gdl', 'anc_visits_count',
        'anc_1_date', 'anc_2_date', 'anc_3_date', 'anc_4_date',
        'lmp_date', 'edd', 'pregnancy_status', 'tt_1_given',
        'tt_2_given', 'ifa_tablets_given', 'urine_albumin',
        'fundal_height_cm', 'delivery_place', 'institutional_delivery',
        'child_weight_kg', 'child_height_cm', 'muac_cm',
        'vaccinated', 'vaccination_date', 'full_immunisation_status',
        'nutritional_status', 'oedema_present', 'pallor_present'
    ],
    'PHC': [
        'name', 'age', 'dob', 'systolic_bp', 'diastolic_bp',
        'weight_kg', 'haemoglobin_gdl', 'anc_visits_count',
        'anc_1_date', 'anc_2_date', 'anc_3_date', 'anc_4_date',
        'lmp_date', 'edd', 'pregnancy_status',
        'urine_albumin', 'fundal_height_cm',
        'blood_sugar_fasting', 'delivery_place',
        'institutional_delivery', 'oedema_present', 'pallor_present'
    ],
    'Anganwadi': [
        'name', 'age', 'dob', 'weight_kg',
        'pregnancy_status', 'child_weight_kg', 'child_height_cm',
        'muac_cm', 'full_immunisation_status', 'vaccinated',
        'vaccination_date', 'nutritional_status',
        'vitamin_a_given', 'oedema_present'
    ]
}


# ── Helper Functions ───────────────────────────────────────────────────────────

def random_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime('%d-%m-%Y')

def date_add_days(date_str, days):
    try:
        d = datetime.strptime(date_str, '%d-%m-%Y')
        return (d + timedelta(days=days)).strftime('%d-%m-%Y')
    except:
        return None

def generate_abha_id():
    return f"{random.randint(10,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def generate_phone():
    return f"+91{random.randint(7000000000, 9999999999)}"

def compute_waz(weight_kg, age_months, gender):
    # Simplified WHO reference median for WAZ
    # Real implementation would use full WHO tables
    median_weight = 3.3 + (age_months * 0.18) if gender == 'M' else 3.2 + (age_months * 0.17)
    sd = 1.0
    return round((weight_kg - median_weight) / sd, 2)

def compute_haz(height_cm, age_months, gender):
    median_height = 50 + (age_months * 1.8) if gender == 'M' else 49.5 + (age_months * 1.75)
    sd = 2.5
    return round((height_cm - median_height) / sd, 2)


# ── Name Generation ────────────────────────────────────────────────────────────

def generate_woman_name():
    first = random.choice(list(KANNADA_NAMES.keys()))
    last = random.choice(KANNADA_SURNAMES)
    variants = KANNADA_NAMES[first]
    true_name = f"{first} {last}"
    cadre_names = {
        'ASHA':      f"{variants[0]} {last}",
        'ANM':       f"{variants[1]} {last}",
        'PHC':       f"{variants[2]} {last}",
        'Anganwadi': f"{variants[3]} {last}"
    }
    return true_name, cadre_names

def generate_child_name(gender):
    if gender == 'M':
        names = ['Raju', 'Suresh', 'Mahesh', 'Ganesh', 'Ramesh',
                 'Kiran', 'Arjun', 'Vijay', 'Anil', 'Sanjay']
    else:
        names = list(KANNADA_NAMES.keys())
    first = random.choice(names)
    last = random.choice(KANNADA_SURNAMES)
    return f"{first} {last}"


# ── Patient Generation ─────────────────────────────────────────────────────────

def generate_woman(patient_id):
    true_name, cadre_names = generate_woman_name()
    age = int(np.clip(np.random.normal(26, 7), 15, 49))
    dob_year = 2025 - age
    dob = random_date(dob_year, dob_year)
    district = random.choice(DISTRICTS)
    taluk = random.choice(TALUKS.get(district, ['Unknown']))
    village = random.choice(VILLAGES)
    caste = np.random.choice(CASTE_CATEGORIES, p=CASTE_PROBS)
    bpl = int(np.random.binomial(1, 0.32))  # 32% BPL in Karnataka rural

    # Pregnancy status — 30% of women aged 15-49 currently pregnant
    preg_prob = 0.30 if 18 <= age <= 35 else 0.10
    pregnancy_status = np.random.choice(
        ['pregnant', 'not_pregnant', 'postpartum'],
        p=[preg_prob, 0.65, 0.05] if preg_prob == 0.30
        else [preg_prob, 0.85, 0.05]
    )

    gravida = random.randint(1, 5)
    parity = max(0, gravida - 1)

    # LMP and EDD
    if pregnancy_status == 'pregnant':
        lmp_date = random_date(2024, 2024)
        lmp_dt = datetime.strptime(lmp_date, '%d-%m-%Y')
        edd_dt = lmp_dt + timedelta(days=280)
        edd = edd_dt.strftime('%d-%m-%Y')
        gestational_age_weeks = int((datetime(2025, 1, 1) - lmp_dt).days / 7)
        gestational_age_weeks = max(4, min(40, gestational_age_weeks))
    else:
        lmp_date = random_date(2023, 2024)
        edd = None
        gestational_age_weeks = None

    # ANC visits
    anc_visits_count = int(np.clip(np.random.poisson(3.5), 0, 8))
    anc_dates = []
    if pregnancy_status == 'pregnant' and lmp_date:
        base = datetime.strptime(lmp_date, '%d-%m-%Y')
        for i in range(min(anc_visits_count, 4)):
            visit = base + timedelta(weeks=12 + i * 8)
            anc_dates.append(visit.strftime('%d-%m-%Y'))
    while len(anc_dates) < 4:
        anc_dates.append(None)

    # Clinical values — NFHS-5 Karnataka
    systolic_bp = int(np.clip(np.random.normal(115, 14), 80, 200))
    diastolic_bp = int(np.clip(np.random.normal(75, 10), 50, 130))
    weight_kg = round(np.clip(np.random.normal(52, 10), 35, 100), 1)
    haemoglobin_gdl = round(np.clip(np.random.normal(10.5, 1.8), 5.0, 16.0), 1)
    urine_albumin = np.random.choice(
        ['negative', 'trace', '1+', '2+'], p=[0.85, 0.08, 0.05, 0.02]
    )
    oedema_present = int(np.random.binomial(1, 0.08))
    pallor_present = int(np.random.binomial(1, 0.35))  # anaemia prevalent
    blood_sugar_fasting = round(np.clip(np.random.normal(88, 15), 60, 200), 1)
    fundal_height_cm = None
    if pregnancy_status == 'pregnant' and gestational_age_weeks:
        fundal_height_cm = round(gestational_age_weeks * 0.9 + random.uniform(-2, 2), 1)

    # TT and IFA
    tt_1_given = int(np.random.binomial(1, 0.85))
    tt_2_given = int(np.random.binomial(1, 0.75)) if tt_1_given else 0
    ifa_tablets_given = random.randint(0, 180)

    # Delivery info
    delivery_place = np.random.choice(
        ['home', 'PHC', 'CHC', 'hospital'],
        p=[0.05, 0.30, 0.25, 0.40]
    )
    delivery_date = random_date(2023, 2024) if pregnancy_status == 'postpartum' else None
    institutional_delivery = int(delivery_place != 'home')

    # High risk — ground truth
    high_risk = int(
        systolic_bp >= 140 or
        haemoglobin_gdl < 7.0 or
        anc_visits_count < 2 or
        (age < 18 or age > 35) or
        urine_albumin in ['1+', '2+'] or
        oedema_present == 1
    )

    high_risk_reasons = []
    if systolic_bp >= 140:
        high_risk_reasons.append('hypertension')
    if haemoglobin_gdl < 7.0:
        high_risk_reasons.append('severe_anaemia')
    if anc_visits_count < 2:
        high_risk_reasons.append('missed_anc')
    if age < 18 or age > 35:
        high_risk_reasons.append('age_risk')
    if urine_albumin in ['1+', '2+']:
        high_risk_reasons.append('proteinuria')
    if oedema_present:
        high_risk_reasons.append('oedema')
    high_risk_reason = '/'.join(high_risk_reasons) if high_risk_reasons else 'none'

    return {
        # Identity
        'patient_id': patient_id,
        'patient_type': 'woman',
        'true_name': true_name,
        'cadre_names': cadre_names,
        'age': age,
        'dob': dob,
        'village': village,
        'district': district,
        'taluk': taluk,
        'gender': 'F',
        'caste_category': caste,
        'bpl_status': bpl,
        'phone_number': generate_phone(),
        'abha_id': generate_abha_id(),
        # Maternal
        'pregnancy_status': pregnancy_status,
        'gravida': gravida,
        'parity': parity,
        'lmp_date': lmp_date,
        'edd': edd,
        'gestational_age_weeks': gestational_age_weeks,
        'anc_visits_count': anc_visits_count,
        'anc_1_date': anc_dates[0],
        'anc_2_date': anc_dates[1],
        'anc_3_date': anc_dates[2],
        'anc_4_date': anc_dates[3],
        'tt_1_given': tt_1_given,
        'tt_2_given': tt_2_given,
        'ifa_tablets_given': ifa_tablets_given,
        'delivery_place': delivery_place,
        'delivery_date': delivery_date,
        'institutional_delivery': institutional_delivery,
        # Clinical
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,
        'weight_kg': weight_kg,
        'haemoglobin_gdl': haemoglobin_gdl,
        'urine_albumin': urine_albumin,
        'oedema_present': oedema_present,
        'pallor_present': pallor_present,
        'blood_sugar_fasting': blood_sugar_fasting,
        'fundal_height_cm': fundal_height_cm,
        # Risk
        'true_high_risk': high_risk,
        'true_high_risk_reason': high_risk_reason,
        # Child fields — None for women
        'child_weight_kg': None,
        'child_height_cm': None,
        'muac_cm': None,
        'waz_score': None,
        'haz_score': None,
        'nutritional_status': None,
        'stunting_status': None,
        'wasting_status': None,
        'full_immunisation_status': None,
        'vaccinated': None,
        'vaccination_date': None,
        'vitamin_a_given': None,
        'mother_patient_id': None,
        'child_age_months': None,
        'child_gender': None,
    }


def generate_child(patient_id, mother_patient_id=None):
    true_name_base, _ = generate_woman_name()
    child_gender = random.choice(['M', 'F'])
    child_name = generate_child_name(child_gender)
    child_age_months = random.randint(0, 59)
    child_dob_year = 2025 - (child_age_months // 12)
    child_dob = random_date(child_dob_year, child_dob_year)

    district = random.choice(DISTRICTS)
    taluk = random.choice(TALUKS.get(district, ['Unknown']))
    village = random.choice(VILLAGES)

    # Growth — NFHS-5 Karnataka
    # Expected weight by age
    median_w = 3.3 + child_age_months * 0.18 if child_gender == 'M' \
        else 3.2 + child_age_months * 0.17
    child_weight_kg = round(
        np.clip(np.random.normal(median_w, 1.2), 2.0, 25.0), 1
    )
    median_h = 50 + child_age_months * 1.8 if child_gender == 'M' \
        else 49.5 + child_age_months * 1.75
    child_height_cm = round(
        np.clip(np.random.normal(median_h, 3.0), 45.0, 120.0), 1
    )
    muac_cm = round(np.clip(np.random.normal(13.5, 1.5), 9.0, 18.0), 1)

    waz = compute_waz(child_weight_kg, child_age_months, child_gender)
    haz = compute_haz(child_height_cm, child_age_months, child_gender)
    whz = round(waz - haz, 2)

    # Nutritional status thresholds
    if muac_cm < 11.5 or waz < -3:
        nutritional_status = 'SAM'
    elif muac_cm < 12.5 or waz < -2:
        nutritional_status = 'MAM'
    else:
        nutritional_status = 'normal'

    stunting_status = 'severe' if haz < -3 else 'moderate' if haz < -2 else 'normal'
    wasting_status = 'severe' if whz < -3 else 'moderate' if whz < -2 else 'normal'

    # Immunisation — NFHS-5 Karnataka 65.2% fully immunised
    full_imm = int(np.random.binomial(1, 0.652))
    vaccinated = full_imm
    vaccination_date = random_date(2023, 2024) if vaccinated else None

    # Individual vaccines
    bcg = 1 if child_age_months >= 1 else 0
    opv_0 = 1 if child_age_months >= 0 else 0
    opv_1 = 1 if child_age_months >= 2 and full_imm else int(np.random.binomial(1, 0.8))
    opv_2 = 1 if child_age_months >= 3 and full_imm else int(np.random.binomial(1, 0.75))
    opv_3 = 1 if child_age_months >= 4 and full_imm else int(np.random.binomial(1, 0.70))
    dpt_1 = opv_1
    dpt_2 = opv_2
    dpt_3 = opv_3
    measles_1 = 1 if child_age_months >= 9 and full_imm else int(np.random.binomial(1, 0.7))
    measles_2 = 1 if child_age_months >= 16 and full_imm else 0
    vitamin_a = 1 if child_age_months >= 9 else 0

    # High risk
    high_risk = int(
        nutritional_status in ['SAM', 'MAM'] or
        waz < -2 or
        (child_age_months >= 12 and not full_imm)
    )

    # Cadre name variants for child
    cadre_names = {
        'ASHA': child_name,
        'ANM': child_name.replace('a', 'a'),
        'PHC': child_name,
        'Anganwadi': child_name.split()[0]  # sometimes only first name
    }

    return {
        # Identity
        'patient_id': patient_id,
        'patient_type': 'child',
        'true_name': child_name,
        'cadre_names': cadre_names,
        'age': round(child_age_months / 12, 1),
        'dob': child_dob,
        'village': village,
        'district': district,
        'taluk': taluk,
        'gender': child_gender,
        'caste_category': np.random.choice(CASTE_CATEGORIES, p=CASTE_PROBS),
        'bpl_status': int(np.random.binomial(1, 0.32)),
        'phone_number': generate_phone(),
        'abha_id': generate_abha_id(),
        'mother_patient_id': mother_patient_id,
        'child_age_months': child_age_months,
        'child_gender': child_gender,
        # Child growth
        'child_weight_kg': child_weight_kg,
        'child_height_cm': child_height_cm,
        'muac_cm': muac_cm,
        'waz_score': waz,
        'haz_score': haz,
        'nutritional_status': nutritional_status,
        'stunting_status': stunting_status,
        'wasting_status': wasting_status,
        # Immunisation
        'full_immunisation_status': 'complete' if full_imm else 'partial',
        'vaccinated': vaccinated,
        'vaccination_date': vaccination_date,
        'bcg_given': bcg,
        'opv_0_given': opv_0,
        'opv_1_given': opv_1,
        'opv_2_given': opv_2,
        'opv_3_given': opv_3,
        'dpt_1_given': dpt_1,
        'dpt_2_given': dpt_2,
        'dpt_3_given': dpt_3,
        'measles_1_given': measles_1,
        'measles_2_given': measles_2,
        'vitamin_a_given': vitamin_a,
        # Risk
        'true_high_risk': high_risk,
        'true_high_risk_reason': nutritional_status if high_risk else 'none',
        # Woman fields — None for children
        'pregnancy_status': None,
        'gravida': None,
        'parity': None,
        'lmp_date': None,
        'edd': None,
        'gestational_age_weeks': None,
        'anc_visits_count': None,
        'anc_1_date': None,
        'anc_2_date': None,
        'anc_3_date': None,
        'anc_4_date': None,
        'tt_1_given': None,
        'tt_2_given': None,
        'ifa_tablets_given': None,
        'delivery_place': None,
        'delivery_date': None,
        'institutional_delivery': None,
        'systolic_bp': None,
        'diastolic_bp': None,
        'weight_kg': None,
        'haemoglobin_gdl': None,
        'urine_albumin': None,
        'oedema_present': None,
        'pallor_present': None,
        'blood_sugar_fasting': None,
        'fundal_height_cm': None,
    }


# ── Conflict Injection ─────────────────────────────────────────────────────────

def inject_conflict(patient, field, cadre):
    """
    Inject a realistic conflict into one field for one cadre.
    Returns (corrupted_value, conflict_type, severity)
    """
    true_val = patient.get(field)
    if true_val is None:
        return None, 'no_conflict', 0

    # Measurement conflicts — numeric fields
    if field == 'systolic_bp':
        error = random.choice([-20, -15, -10, 10, 15, 20])
        severity = 3 if abs(error) >= 20 else 2
        return int(true_val + error), 'measurement_conflict', severity

    elif field == 'diastolic_bp':
        error = random.choice([-10, -8, 8, 10])
        return int(true_val + error), 'measurement_conflict', 2

    elif field == 'weight_kg':
        error = random.choice([-5, -3, 3, 5])
        return round(true_val + error, 1), 'measurement_conflict', 1

    elif field == 'haemoglobin_gdl':
        error = random.choice([-2.0, -1.5, 1.5, 2.0])
        val = round(np.clip(true_val + error, 5.0, 16.0), 1)
        severity = 3 if val < 7.0 else 2
        return val, 'measurement_conflict', severity

    elif field == 'anc_visits_count':
        error = random.choice([-2, -1, 1, 2])
        return max(0, int(true_val + error)), 'measurement_conflict', 2

    elif field == 'child_weight_kg':
        error = random.choice([-2.0, -1.0, 1.0, 2.0])
        return round(max(2.0, true_val + error), 1), 'measurement_conflict', 2

    elif field == 'child_height_cm':
        error = random.choice([-3.0, -2.0, 2.0, 3.0])
        return round(max(45.0, true_val + error), 1), 'measurement_conflict', 1

    elif field == 'muac_cm':
        error = random.choice([-1.5, -1.0, 1.0, 1.5])
        return round(max(9.0, true_val + error), 1), 'measurement_conflict', 2

    elif field == 'age':
        error = random.choice([-3, -2, -1, 1, 2, 3])
        return max(1, int(true_val + error)), 'identity_conflict', 1

    elif field == 'blood_sugar_fasting':
        error = random.choice([-20, -10, 10, 20])
        return round(true_val + error, 1), 'measurement_conflict', 2

    # Categorical conflicts
    elif field == 'vaccinated':
        return 1 - int(true_val), 'measurement_conflict', 3

    elif field == 'full_immunisation_status':
        options = ['complete', 'partial', 'not_started']
        options.remove(true_val) if true_val in options else None
        return random.choice(options), 'measurement_conflict', 3

    elif field == 'pregnancy_status':
        options = ['pregnant', 'not_pregnant', 'postpartum']
        if true_val in options:
            options.remove(true_val)
        return random.choice(options), 'measurement_conflict', 3

    elif field == 'nutritional_status':
        options = ['normal', 'MAM', 'SAM']
        if true_val in options:
            options.remove(true_val)
        return random.choice(options), 'measurement_conflict', 3

    elif field == 'urine_albumin':
        options = ['negative', 'trace', '1+', '2+']
        if true_val in options:
            options.remove(true_val)
        return random.choice(options), 'measurement_conflict', 2

    elif field == 'delivery_place':
        options = ['home', 'PHC', 'CHC', 'hospital']
        if true_val in options:
            options.remove(true_val)
        return random.choice(options), 'measurement_conflict', 1

    # Temporal conflicts — date fields
    elif field in ['anc_1_date', 'anc_2_date', 'anc_3_date', 'anc_4_date',
                   'vaccination_date', 'lmp_date', 'delivery_date']:
        if true_val is None:
            return None, 'no_conflict', 0
        shift_days = random.choice([-30, -14, -7, 7, 14, 30])
        shifted = date_add_days(true_val, shift_days)
        severity = 3 if abs(shift_days) >= 30 else 2 if abs(shift_days) >= 14 else 1
        return shifted, 'temporal_conflict', severity

    # Missing conflicts
    elif field in CADRE_RESPONSIBLE_FIELDS.get(cadre, []):
        return None, 'missing_conflict', 2

    return true_val, 'no_conflict', 0


def generate_cadre_record(patient, cadre, conflict_rate=0.22):
    """Generate one cadre's record for a patient with possible conflict."""

    record = {
        'patient_id': patient['patient_id'],
        'patient_type': patient['patient_type'],
        'cadre': cadre,
        'data_source': cadre,
        'visit_date': random_date(2024, 2025),
        'record_entry_date': random_date(2024, 2025),

        # Identity — cadre-specific name variant
        'name': patient['cadre_names'][cadre],
        'age': patient['age'],
        'dob': patient['dob'],
        'village': patient['village'],
        'district': patient['district'],
        'taluk': patient['taluk'],
        'gender': patient['gender'],
        'caste_category': patient['caste_category'],
        'bpl_status': patient['bpl_status'],
        'phone_number': patient['phone_number'],
        'abha_id': patient['abha_id'],
        'mother_patient_id': patient.get('mother_patient_id'),
        'child_age_months': patient.get('child_age_months'),
        'child_gender': patient.get('child_gender'),

        # Clinical values — start with true values
        'pregnancy_status': patient.get('pregnancy_status'),
        'gravida': patient.get('gravida'),
        'parity': patient.get('parity'),
        'lmp_date': patient.get('lmp_date'),
        'edd': patient.get('edd'),
        'gestational_age_weeks': patient.get('gestational_age_weeks'),
        'anc_visits_count': patient.get('anc_visits_count'),
        'anc_1_date': patient.get('anc_1_date'),
        'anc_2_date': patient.get('anc_2_date'),
        'anc_3_date': patient.get('anc_3_date'),
        'anc_4_date': patient.get('anc_4_date'),
        'tt_1_given': patient.get('tt_1_given'),
        'tt_2_given': patient.get('tt_2_given'),
        'ifa_tablets_given': patient.get('ifa_tablets_given'),
        'delivery_place': patient.get('delivery_place'),
        'delivery_date': patient.get('delivery_date'),
        'institutional_delivery': patient.get('institutional_delivery'),
        'systolic_bp': patient.get('systolic_bp'),
        'diastolic_bp': patient.get('diastolic_bp'),
        'weight_kg': patient.get('weight_kg'),
        'haemoglobin_gdl': patient.get('haemoglobin_gdl'),
        'urine_albumin': patient.get('urine_albumin'),
        'oedema_present': patient.get('oedema_present'),
        'pallor_present': patient.get('pallor_present'),
        'blood_sugar_fasting': patient.get('blood_sugar_fasting'),
        'fundal_height_cm': patient.get('fundal_height_cm'),
        'child_weight_kg': patient.get('child_weight_kg'),
        'child_height_cm': patient.get('child_height_cm'),
        'muac_cm': patient.get('muac_cm'),
        'waz_score': patient.get('waz_score'),
        'haz_score': patient.get('haz_score'),
        'nutritional_status': patient.get('nutritional_status'),
        'stunting_status': patient.get('stunting_status'),
        'wasting_status': patient.get('wasting_status'),
        'full_immunisation_status': patient.get('full_immunisation_status'),
        'vaccinated': patient.get('vaccinated'),
        'vaccination_date': patient.get('vaccination_date'),
        'vitamin_a_given': patient.get('vitamin_a_given'),
        'bcg_given': patient.get('bcg_given'),
        'opv_0_given': patient.get('opv_0_given'),
        'opv_1_given': patient.get('opv_1_given'),
        'opv_2_given': patient.get('opv_2_given'),
        'opv_3_given': patient.get('opv_3_given'),
        'dpt_1_given': patient.get('dpt_1_given'),
        'dpt_2_given': patient.get('dpt_2_given'),
        'dpt_3_given': patient.get('dpt_3_given'),
        'measles_1_given': patient.get('measles_1_given'),
        'measles_2_given': patient.get('measles_2_given'),

        # Set fields NOT in this cadre's responsibility to None
        # (legitimate missing — not a conflict)
        'conflict_type': 'no_conflict',
        'conflict_field': None,
        'severity_score': 0,

        # Ground truth for evaluation
        'true_high_risk': patient['true_high_risk'],
        'true_high_risk_reason': patient['true_high_risk_reason'],
    }

    # Null out fields this cadre does not record
    responsible = CADRE_RESPONSIBLE_FIELDS[cadre]
    all_clinical = [
        'systolic_bp', 'diastolic_bp', 'weight_kg', 'haemoglobin_gdl',
        'anc_visits_count', 'anc_1_date', 'anc_2_date', 'anc_3_date',
        'anc_4_date', 'lmp_date', 'edd', 'pregnancy_status',
        'tt_1_given', 'tt_2_given', 'ifa_tablets_given',
        'urine_albumin', 'fundal_height_cm', 'delivery_place',
        'institutional_delivery', 'blood_sugar_fasting',
        'child_weight_kg', 'child_height_cm', 'muac_cm',
        'vaccinated', 'vaccination_date', 'full_immunisation_status',
        'nutritional_status', 'oedema_present', 'pallor_present',
        'vitamin_a_given'
    ]
    for f in all_clinical:
        if f not in responsible:
            record[f] = None

    # Inject conflict with given probability
    if random.random() < conflict_rate:
        injectable = [
            f for f in responsible
            if f not in ['name', 'gender', 'abha_id', 'phone_number']
            and record.get(f) is not None
        ]
        if injectable:
            chosen_field = random.choice(injectable)
            corrupted, ctype, severity = inject_conflict(
                patient, chosen_field, cadre
            )
            record[chosen_field] = corrupted
            record['conflict_type'] = ctype
            record['conflict_field'] = chosen_field
            record['severity_score'] = severity

    return record


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    os.makedirs('data/synthetic', exist_ok=True)
    os.makedirs('data/nfhs5_reference', exist_ok=True)

    N_WOMEN = 7000
    N_CHILDREN = 3000
    N_TOTAL = N_WOMEN + N_CHILDREN

    print(f"Generating {N_WOMEN} women and {N_CHILDREN} children...")
    print(f"Total patients: {N_TOTAL}")
    print(f"Total cadre records: {N_TOTAL * 4}")
    print()

    # Generate women
    women = []
    for i in range(N_WOMEN):
        pid = f"W{i+1:05d}"
        women.append(generate_woman(pid))
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i+1}/{N_WOMEN} women...")

    # Generate children — link ~50% to a random mother
    pregnant_ids = [
        w['patient_id'] for w in women
        if w['pregnancy_status'] in ['pregnant', 'postpartum']
    ]
    children = []
    for i in range(N_CHILDREN):
        pid = f"C{i+1:05d}"
        mother_id = random.choice(pregnant_ids) if random.random() < 0.5 \
            and pregnant_ids else None
        children.append(generate_child(pid, mother_id))
        if (i + 1) % 500 == 0:
            print(f"  Generated {i+1}/{N_CHILDREN} children...")

    all_patients = women + children

    # Generate cadre records
    print("\nGenerating cadre records with conflict injection...")
    all_records = []
    for idx, patient in enumerate(all_patients):
        for cadre in CADRES:
            record = generate_cadre_record(patient, cadre, conflict_rate=0.22)
            all_records.append(record)
        if (idx + 1) % 2000 == 0:
            print(f"  Processed {idx+1}/{N_TOTAL} patients...")

    df_records = pd.DataFrame(all_records)

    # Save cadre records
    df_records.to_csv('data/synthetic/cadre_records.csv', index=False)
    print(f"\nSaved: data/synthetic/cadre_records.csv")

    # Save ground truth
    ground_truth_rows = []
    for p in all_patients:
        ground_truth_rows.append({
            'patient_id': p['patient_id'],
            'patient_type': p['patient_type'],
            'true_name': p['true_name'],
            'true_high_risk': p['true_high_risk'],
            'true_high_risk_reason': p['true_high_risk_reason'],
            'true_systolic_bp': p.get('systolic_bp'),
            'true_diastolic_bp': p.get('diastolic_bp'),
            'true_weight_kg': p.get('weight_kg'),
            'true_haemoglobin_gdl': p.get('haemoglobin_gdl'),
            'true_anc_visits_count': p.get('anc_visits_count'),
            'true_vaccinated': p.get('vaccinated'),
            'true_full_immunisation_status': p.get('full_immunisation_status'),
            'true_waz_score': p.get('waz_score'),
            'true_nutritional_status': p.get('nutritional_status'),
        })

    df_gt = pd.DataFrame(ground_truth_rows)
    df_gt.to_csv('data/synthetic/ground_truth.csv', index=False)
    print(f"Saved: data/synthetic/ground_truth.csv")

    # Summary statistics
    conflict_records = df_records[df_records['conflict_type'] != 'no_conflict']
    print(f"\n{'='*50}")
    print(f"DATASET SUMMARY")
    print(f"{'='*50}")
    print(f"Total patients        : {N_TOTAL:,}")
    print(f"  Women               : {N_WOMEN:,}")
    print(f"  Children            : {N_CHILDREN:,}")
    print(f"Total cadre records   : {len(df_records):,}")
    print(f"Conflict records      : {len(conflict_records):,} "
          f"({100*len(conflict_records)/len(df_records):.1f}%)")
    print(f"\nConflict type breakdown:")
    print(df_records['conflict_type'].value_counts().to_string())
    print(f"\nSeverity breakdown:")
    print(df_records['severity_score'].value_counts().sort_index().to_string())
    print(f"\nHigh risk patients    : {df_gt['true_high_risk'].sum():,} "
          f"({100*df_gt['true_high_risk'].mean():.1f}%)")
    print(f"\nWomen — pregnancy status:")
    women_df = df_records[
        (df_records['patient_type'] == 'woman') &
        (df_records['cadre'] == 'ASHA')
    ]
    print(women_df['pregnancy_status'].value_counts().to_string())
    print(f"\nChildren — nutritional status:")
    children_df = df_records[
        (df_records['patient_type'] == 'child') &
        (df_records['cadre'] == 'Anganwadi')
    ]
    print(children_df['nutritional_status'].value_counts().to_string())


if __name__ == '__main__':
    main()