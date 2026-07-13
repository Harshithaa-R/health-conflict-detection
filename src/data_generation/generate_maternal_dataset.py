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

NUM_MATERNAL  = 5000
NUM_CHILD     = 4000
NUM_CHRONIC   = 4000   # will be split into subtypes below

# Chronic disease subtype distribution (realistic Karnataka prevalence)
# Diabetes only        : 28%
# Hypertension only    : 27%
# TB only              : 20%
# Diabetes+Hypertension: 18%
# TB+Diabetes          :  4%
# TB+Hypertension      :  3%
CHRONIC_SUBTYPES = [
    "diabetes",
    "hypertension",
    "tb",
    "diabetes_hypertension",
    "tb_diabetes",
    "tb_hypertension",
]
CHRONIC_PROBS = [0.28, 0.27, 0.20, 0.18, 0.04, 0.03]

LOCATIONS = [
    ("Tumkur",          "Eeramaranahalli", "Sira"),
    ("Tumkur",          "Kora",            "Gubbi"),
    ("Tumkur",          "Handanakere",     "Turuvekere"),
    ("Mysore",          "Nanjangud",       "Nanjangud"),
    ("Mysore",          "Hunsur",          "Hunsur"),
    ("Mysore",          "Saligrama",       "K R Nagar"),
    ("Mandya",          "Maddur",          "Maddur"),
    ("Mandya",          "Malavalli",       "Malavalli"),
    ("Mandya",          "Nagamangala",     "Nagamangala"),
    ("Kolar",           "Mulbagal",        "Mulbagal"),
    ("Kolar",           "Bangarpet",       "Bangarpet"),
    ("Kolar",           "Malur",           "Malur"),
    ("Hassan",          "Arsikere",        "Arsikere"),
    ("Hassan",          "Belur",           "Belur"),
    ("Hassan",          "Sakleshpur",      "Sakleshpur"),
    ("Davanagere",      "Harihar",         "Harihar"),
    ("Davanagere",      "Honnali",         "Honnali"),
    ("Davanagere",      "Jagalur",         "Jagalur"),
    ("Chikkaballapur",  "Bagepalli",       "Bagepalli"),
    ("Chikkaballapur",  "Sidlaghatta",     "Sidlaghatta"),
    ("Chikkaballapur",  "Gudibande",       "Gudibande"),
    ("Kalaburagi",      "Chincholi",       "Chincholi"),
    ("Kalaburagi",      "Sedam",           "Sedam"),
    ("Kalaburagi",      "Jewargi",         "Jewargi"),
    ("Shivamogga",      "Bhadravati",      "Bhadravati"),
    ("Shivamogga",      "Sagar",           "Sagar"),
    ("Shivamogga",      "Shikaripura",     "Shikaripura"),
    ("Belagavi",        "Gokak",           "Gokak"),
    ("Belagavi",        "Athani",          "Athani"),
    ("Belagavi",        "Ramdurg",         "Ramdurg"),
]

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def random_date(start_days=0, end_days=250):
    today = datetime.today()
    delta = random.randint(start_days, end_days)
    return (today - timedelta(days=delta)).strftime('%d-%m-%Y')


def calculate_edd(lmp_date):
    lmp = datetime.strptime(lmp_date, '%d-%m-%Y')
    return (lmp + timedelta(days=280)).strftime('%d-%m-%Y')


def transliterate_name(name):
    # Realistic Kannada-English phonetic variants
    variations = {
        "Savitha":  "Savita",
        "Lakshmi":  "Laxmi",
        "Krishna":  "Crishna",
        "Radha":    "Radhamma",
        "Geetha":   "Gita",
        "Shwetha":  "Swetha",
        "Kavitha":  "Kavita",
        "Suma":     "Sooma",
        "Rekha":    "Rekamma",
        "Pushpa":   "Pushpamma",
        "Manjula":  "Manjamma",
        "Sunitha":  "Sunita",
        "Anitha":   "Anita",
        "Nirmala":  "Nirmamma",
        "Shantha":  "Shanta",
    }
    parts = name.split()
    if parts:
        first = parts[0]
        if first in variations:
            parts[0] = variations[first]
    return " ".join(parts)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def add_noise(val, sigma, lo, hi, prob=1.0):
    if random.random() < prob:
        return round(clamp(val + np.random.normal(0, sigma), lo, hi), 1)
    return val


def flip_bool(val, prob):
    if random.random() < prob:
        return 1 - val
    return val


# ---------------------------------------------------
# NULL MASK — realistic missingness per cadre
# ---------------------------------------------------

def maybe_null(val, cadre, field):
    """
    Return None if this cadre realistically wouldn't
    record this field. Based on the cadre-field mapping.
    """
    nulls = {
        # (cadre, field) -> probability of being null
        ("ASHA",      "haemoglobin_gdl"):        0.60,
        ("ASHA",      "blood_sugar_fasting"):     0.80,
        ("ASHA",      "fundal_height_cm"):        0.90,
        ("ASHA",      "urine_albumin"):           0.95,
        ("ASHA",      "hba1c"):                   1.00,
        ("ASHA",      "postprandial_blood_sugar"): 1.00,
        ("ASHA",      "creatinine"):              1.00,
        ("ASHA",      "potassium"):               1.00,
        ("ASHA",      "fundoscopy_done"):         1.00,
        ("ASHA",      "ecg_done"):                1.00,
        ("ASHA",      "genexpert_result"):        1.00,
        ("ASHA",      "chest_xray_result"):       1.00,
        ("ASHA",      "sputum_smear_result"):     0.90,
        ("ASHA",      "hiv_coinfection"):         1.00,
        ("ASHA",      "waist_circumference"):     1.00,
        ("ASHA",      "waz_score"):               0.80,
        ("ASHA",      "haz_score"):               0.80,
        ("ASHA",      "haemoglobin_child"):       0.90,
        ("ANM",       "hba1c"):                   1.00,
        ("ANM",       "creatinine"):              1.00,
        ("ANM",       "potassium"):               1.00,
        ("ANM",       "fundoscopy_done"):         1.00,
        ("ANM",       "ecg_done"):                1.00,
        ("ANM",       "genexpert_result"):        1.00,
        ("ANM",       "chest_xray_result"):       1.00,
        ("ANM",       "hiv_coinfection"):         0.80,
        ("ANM",       "postprandial_blood_sugar"): 0.40,
        ("ANM",       "blood_sugar_fasting"):     0.20,
        ("ANM",       "waist_circumference"):     0.50,
        ("ANM",       "haemoglobin_child"):       0.40,
        ("ANGANWADI", "haemoglobin_gdl"):         1.00,
        ("ANGANWADI", "blood_sugar_fasting"):     1.00,
        ("ANGANWADI", "fundal_height_cm"):        1.00,
        ("ANGANWADI", "urine_albumin"):           1.00,
        ("ANGANWADI", "haemoglobin_child"):       1.00,
    }
    p = nulls.get((cadre, field), 0.0)
    if random.random() < p:
        return None
    return val


# ===================================================
# 1. MATERNAL PATIENTS  (W00001 – W05000)
# ===================================================

def generate_maternal_patients():

    print("Generating maternal patients...")

    patients = []

    for i in range(1, NUM_MATERNAL + 1):

        pid              = f"W{i:05d}"
        district, village, taluk = random.choice(LOCATIONS)
        name             = fake.name_female()
        age              = random.randint(18, 40)
        dob              = (datetime.today() - timedelta(days=age*365)).strftime('%d-%m-%Y')
        gender           = "F"
        gravida          = random.randint(1, 5)
        parity           = max(0, gravida - 1)
        gestational_age  = random.randint(6, 40)
        lmp              = (datetime.today() - timedelta(days=gestational_age*7)).strftime('%d-%m-%Y')
        edd              = calculate_edd(lmp)

        systolic_bp  = int(clamp(np.random.normal(118, 12), 88, 175))
        diastolic_bp = int(clamp(np.random.normal(76, 8),   50, 120))
        hb           = round(clamp(np.random.normal(10.8, 1.3), 6.0, 14.5), 1)
        weight       = round(clamp(np.random.normal(58, 10), 38, 98), 1)
        anc_visits   = int(np.random.choice([1,2,3,4,5,6], p=[0.05,0.10,0.20,0.35,0.20,0.10]))
        fundal_ht    = round(clamp(np.random.normal(28, 5), 10, 42), 1)
        blood_sugar  = round(clamp(np.random.normal(95, 20), 60, 230), 1)
        urine_alb    = np.random.choice(["negative","trace","positive"], p=[0.75,0.20,0.05])
        oedema       = int(np.random.choice([0,1], p=[0.88,0.12]))
        pallor       = 1 if hb < 9 else 0
        tt1          = random.choice([0,1])
        tt2          = random.choice([0,1])
        ifa          = random.randint(30, 180)

        # Risk
        high_risk = 0
        risk_reasons = []
        if hb < 9:           high_risk = 1; risk_reasons.append("severe_anaemia")
        if systolic_bp > 140: high_risk = 1; risk_reasons.append("hypertension_risk")
        if blood_sugar > 140: high_risk = 1; risk_reasons.append("diabetes_risk")
        if gestational_age > 34 and anc_visits < 2:
            high_risk = 1; risk_reasons.append("missed_anc")
        if weight < 45:      high_risk = 1; risk_reasons.append("low_weight_risk")

        patients.append({
            "patient_id":            pid,
            "domain":                "maternal",
            "patient_type":          "pregnant_woman",
            "name":                  name,
            "age":                   age,
            "dob":                   dob,
            "gender":                gender,
            "district":              district,
            "village":               village,
            "taluk":                 taluk,
            "visit_date":            random_date(0, 180),
            "record_entry_date":     random_date(0, 200),
            # maternal fields
            "gravida":               gravida,
            "parity":                parity,
            "lmp_date":              lmp,
            "edd":                   edd,
            "gestational_age_weeks": gestational_age,
            "anc_visits_count":      anc_visits,
            "systolic_bp":           systolic_bp,
            "diastolic_bp":          diastolic_bp,
            "weight_kg":             weight,
            "haemoglobin_gdl":       hb,
            "urine_albumin":         urine_alb,
            "oedema_present":        oedema,
            "pallor_present":        pallor,
            "blood_sugar_fasting":   blood_sugar,
            "fundal_height_cm":      fundal_ht,
            "tt_1_given":            tt1,
            "tt_2_given":            tt2,
            "ifa_tablets_given":     ifa,
            # child fields — null
            "child_age_months":      None,
            "weight_child_kg":       None,
            "height_cm":             None,
            "muac_cm":               None,
            "waz_score":             None,
            "haz_score":             None,
            "sam_status":            None,
            "haemoglobin_child":     None,
            "bcg_given":             None,
            "opv0_given":            None,
            "opv1_given":            None,
            "opv2_given":            None,
            "opv3_given":            None,
            "dpt1_given":            None,
            "dpt2_given":            None,
            "dpt3_given":            None,
            "hepatitis_b_given":     None,
            "measles_given":         None,
            "mmr_given":             None,
            "pentavalent_given":     None,
            "vitamin_a_given":       None,
            "ifa_child_given":       None,
            "deworming_given":       None,
            "developmental_milestone_met": None,
            # chronic fields — null
            "chronic_condition":     None,
            "fasting_blood_sugar":   None,
            "postprandial_blood_sugar": None,
            "hba1c":                 None,
            "random_blood_glucose":  None,
            "insulin_dependent":     None,
            "diabetes_medication_adherence": None,
            "bmi":                   None,
            "waist_circumference":   None,
            "foot_examination_done": None,
            "eye_examination_done":  None,
            "creatinine":            None,
            "urine_microalbumin":    None,
            "bp_systolic_reading1":  None,
            "bp_systolic_reading2":  None,
            "bp_diastolic_reading1": None,
            "bp_diastolic_reading2": None,
            "pulse_rate":            None,
            "hypertension_medication_adherence": None,
            "medication_name":       None,
            "salt_intake_compliant": None,
            "physical_activity_compliant": None,
            "fundoscopy_done":       None,
            "ecg_done":              None,
            "potassium":             None,
            "sputum_smear_result":   None,
            "genexpert_result":      None,
            "chest_xray_result":     None,
            "treatment_category":    None,
            "treatment_phase":       None,
            "dots_provider":         None,
            "missed_doses_count":    None,
            "tb_weight_kg":          None,
            "side_effects_reported": None,
            "hiv_coinfection":       None,
            "contact_tracing_done":  None,
            # labels
            "true_high_risk":        high_risk,
            "true_high_risk_reason": ",".join(risk_reasons) if risk_reasons else "none",
        })

    return patients


# ===================================================
# 2. CHILD PATIENTS  (C00001 – C04000)
# ===================================================

def generate_child_patients():

    print("Generating child patients...")

    patients = []

    for i in range(1, NUM_CHILD + 1):

        pid              = f"C{i:05d}"
        district, village, taluk = random.choice(LOCATIONS)
        gender           = random.choice(["M", "F"])
        name             = fake.name_male() if gender == "M" else fake.name_female()
        age_months       = random.randint(0, 143)   # 0–11 years 11 months
        age_years        = age_months // 12
        dob              = (datetime.today() - timedelta(days=age_months*30)).strftime('%d-%m-%Y')

        # Anthropometric — WHO standards approximate
        expected_weight  = 3.5 + age_months * 0.18 if age_months < 12 else 9 + (age_months-12)*0.15
        weight           = round(clamp(np.random.normal(expected_weight, expected_weight*0.12), 2.5, 55), 1)
        expected_height  = 50 + age_months * 1.5 if age_months < 12 else 75 + (age_months-12)*0.8
        height           = round(clamp(np.random.normal(expected_height, expected_height*0.04), 45, 150), 1)
        muac             = round(clamp(np.random.normal(14.5, 1.5), 9.5, 20.0), 1)

        # Z-scores
        waz              = round(np.random.normal(-0.5, 1.2), 2)
        haz              = round(np.random.normal(-0.8, 1.3), 2)
        sam              = 1 if muac < 11.5 or waz < -3 else 0

        hb_child         = round(clamp(np.random.normal(11.2, 1.1), 7.0, 14.5), 1)

        # Immunization — age-appropriate coverage
        # Older children more likely to have completed vaccines
        coverage_prob    = min(0.90, 0.5 + age_months * 0.005)
        bcg              = 1 if age_months >= 0 and random.random() < coverage_prob else 0
        opv0             = 1 if age_months >= 0 and random.random() < coverage_prob else 0
        opv1             = 1 if age_months >= 6 and random.random() < coverage_prob else 0
        opv2             = 1 if age_months >= 10 and random.random() < coverage_prob else 0
        opv3             = 1 if age_months >= 14 and random.random() < coverage_prob else 0
        dpt1             = 1 if age_months >= 6 and random.random() < coverage_prob else 0
        dpt2             = 1 if age_months >= 10 and random.random() < coverage_prob else 0
        dpt3             = 1 if age_months >= 14 and random.random() < coverage_prob else 0
        hepb             = 1 if age_months >= 6 and random.random() < coverage_prob else 0
        measles          = 1 if age_months >= 9 and random.random() < coverage_prob else 0
        mmr              = 1 if age_months >= 15 and random.random() < coverage_prob else 0
        pentavalent      = 1 if age_months >= 6 and random.random() < coverage_prob else 0
        vitamin_a        = 1 if age_months >= 9 and random.random() < 0.70 else 0
        ifa_child        = 1 if age_months >= 6 and random.random() < 0.65 else 0
        deworming        = 1 if age_months >= 12 and random.random() < 0.60 else 0
        milestone_met    = 1 if random.random() < 0.88 else 0

        # Risk
        high_risk = 0
        risk_reasons = []
        if sam:               high_risk = 1; risk_reasons.append("severe_acute_malnutrition")
        if hb_child < 9:      high_risk = 1; risk_reasons.append("anaemia")
        if waz < -2:          high_risk = 1; risk_reasons.append("underweight")
        if haz < -2:          high_risk = 1; risk_reasons.append("stunting")
        if not milestone_met: high_risk = 1; risk_reasons.append("developmental_delay")

        patients.append({
            "patient_id":            pid,
            "domain":                "child",
            "patient_type":          "child",
            "name":                  name,
            "age":                   age_years,
            "dob":                   dob,
            "gender":                gender,
            "district":              district,
            "village":               village,
            "taluk":                 taluk,
            "visit_date":            random_date(0, 120),
            "record_entry_date":     random_date(0, 150),
            # maternal fields — null
            "gravida":               None,
            "parity":                None,
            "lmp_date":              None,
            "edd":                   None,
            "gestational_age_weeks": None,
            "anc_visits_count":      None,
            "systolic_bp":           None,
            "diastolic_bp":          None,
            "weight_kg":             None,
            "haemoglobin_gdl":       None,
            "urine_albumin":         None,
            "oedema_present":        None,
            "pallor_present":        None,
            "blood_sugar_fasting":   None,
            "fundal_height_cm":      None,
            "tt_1_given":            None,
            "tt_2_given":            None,
            "ifa_tablets_given":     None,
            # child fields
            "child_age_months":      age_months,
            "weight_child_kg":       weight,
            "height_cm":             height,
            "muac_cm":               muac,
            "waz_score":             waz,
            "haz_score":             haz,
            "sam_status":            sam,
            "haemoglobin_child":     hb_child,
            "bcg_given":             bcg,
            "opv0_given":            opv0,
            "opv1_given":            opv1,
            "opv2_given":            opv2,
            "opv3_given":            opv3,
            "dpt1_given":            dpt1,
            "dpt2_given":            dpt2,
            "dpt3_given":            dpt3,
            "hepatitis_b_given":     hepb,
            "measles_given":         measles,
            "mmr_given":             mmr,
            "pentavalent_given":     pentavalent,
            "vitamin_a_given":       vitamin_a,
            "ifa_child_given":       ifa_child,
            "deworming_given":       deworming,
            "developmental_milestone_met": milestone_met,
            # chronic fields — null
            "chronic_condition":     None,
            "fasting_blood_sugar":   None,
            "postprandial_blood_sugar": None,
            "hba1c":                 None,
            "random_blood_glucose":  None,
            "insulin_dependent":     None,
            "diabetes_medication_adherence": None,
            "bmi":                   None,
            "waist_circumference":   None,
            "foot_examination_done": None,
            "eye_examination_done":  None,
            "creatinine":            None,
            "urine_microalbumin":    None,
            "bp_systolic_reading1":  None,
            "bp_systolic_reading2":  None,
            "bp_diastolic_reading1": None,
            "bp_diastolic_reading2": None,
            "pulse_rate":            None,
            "hypertension_medication_adherence": None,
            "medication_name":       None,
            "salt_intake_compliant": None,
            "physical_activity_compliant": None,
            "fundoscopy_done":       None,
            "ecg_done":              None,
            "potassium":             None,
            "sputum_smear_result":   None,
            "genexpert_result":      None,
            "chest_xray_result":     None,
            "treatment_category":    None,
            "treatment_phase":       None,
            "dots_provider":         None,
            "missed_doses_count":    None,
            "tb_weight_kg":          None,
            "side_effects_reported": None,
            "hiv_coinfection":       None,
            "contact_tracing_done":  None,
            # labels
            "true_high_risk":        high_risk,
            "true_high_risk_reason": ",".join(risk_reasons) if risk_reasons else "none",
        })

    return patients


# ===================================================
# 3. CHRONIC DISEASE PATIENTS  (D00001 – D04000)
# ===================================================

def generate_chronic_patients():

    print("Generating chronic disease patients...")

    patients = []

    for i in range(1, NUM_CHRONIC + 1):

        pid              = f"D{i:05d}"
        district, village, taluk = random.choice(LOCATIONS)
        gender           = random.choice(["M", "F"])
        name             = fake.name_male() if gender == "M" else fake.name_female()
        age              = random.randint(30, 75)
        dob              = (datetime.today() - timedelta(days=age*365)).strftime('%d-%m-%Y')
        subtype          = np.random.choice(CHRONIC_SUBTYPES, p=CHRONIC_PROBS)

        has_diabetes     = "diabetes" in subtype
        has_hypertension = "hypertension" in subtype
        has_tb           = "tb" in subtype

        bmi              = round(clamp(np.random.normal(26, 4), 16, 42), 1)
        waist            = round(clamp(np.random.normal(90 if gender=="M" else 85, 10), 60, 130), 1)

        # Diabetes fields
        if has_diabetes:
            fbs          = round(clamp(np.random.normal(160, 40), 90, 380), 1)
            ppbs         = round(clamp(np.random.normal(220, 50), 120, 450), 1)
            hba1c        = round(clamp(np.random.normal(8.2, 1.5), 5.5, 14.0), 1)
            rbg          = round(clamp(np.random.normal(190, 45), 100, 400), 1)
            insulin_dep  = int(np.random.choice([0,1], p=[0.70,0.30]))
            dm_adhere    = int(np.random.choice([0,1], p=[0.30,0.70]))
            foot_exam    = int(np.random.choice([0,1], p=[0.55,0.45]))
            eye_exam     = int(np.random.choice([0,1], p=[0.50,0.50]))
            creatinine   = round(clamp(np.random.normal(1.1, 0.4), 0.5, 4.5), 2)
            microalb     = round(clamp(np.random.normal(45, 30), 5, 300), 1)
        else:
            fbs = ppbs = hba1c = rbg = None
            insulin_dep = dm_adhere = foot_exam = eye_exam = None
            creatinine = microalb = None

        # Hypertension fields
        if has_hypertension:
            sbp1         = int(clamp(np.random.normal(148, 18), 100, 200))
            sbp2         = int(clamp(np.random.normal(148, 18), 100, 200))
            dbp1         = int(clamp(np.random.normal(92, 12),  60, 130))
            dbp2         = int(clamp(np.random.normal(92, 12),  60, 130))
            pulse        = int(clamp(np.random.normal(80, 10),  55, 120))
            htn_adhere   = int(np.random.choice([0,1], p=[0.25,0.75]))
            med_name     = random.choice(["Amlodipine","Enalapril","Losartan","Telmisartan","Metoprolol"])
            salt_comp    = int(np.random.choice([0,1], p=[0.40,0.60]))
            phys_act     = int(np.random.choice([0,1], p=[0.45,0.55]))
            fundoscopy   = int(np.random.choice([0,1], p=[0.60,0.40]))
            ecg          = int(np.random.choice([0,1], p=[0.55,0.45]))
            potassium    = round(clamp(np.random.normal(4.1, 0.5), 3.0, 6.0), 1)
            creatinine   = round(clamp(np.random.normal(1.0, 0.3), 0.5, 3.5), 2) if creatinine is None else creatinine
        else:
            sbp1 = sbp2 = dbp1 = dbp2 = pulse = None
            htn_adhere = med_name = salt_comp = phys_act = None
            fundoscopy = ecg = potassium = None

        # TB fields
        if has_tb:
            sputum       = random.choice(["positive","negative","scanty"])
            genexpert    = random.choice(["MTB detected","MTB not detected","MTB detected RR"])
            xray         = random.choice(["consolidation","cavitation","normal","miliary"])
            tx_cat       = random.choice(["new","retreatment"])
            tx_phase     = random.choice(["intensive","continuation"])
            dots_prov    = random.choice(["ASHA","ANM","PHC"])
            missed_doses = int(clamp(np.random.normal(3, 4), 0, 30))
            tb_weight    = round(clamp(np.random.normal(52, 10), 30, 85), 1)
            side_effects = int(np.random.choice([0,1], p=[0.55,0.45]))
            hiv          = int(np.random.choice([0,1], p=[0.88,0.12]))
            contact_tr   = int(np.random.choice([0,1], p=[0.35,0.65]))
        else:
            sputum = genexpert = xray = tx_cat = tx_phase = None
            dots_prov = missed_doses = tb_weight = None
            side_effects = hiv = contact_tr = None

        # Risk
        high_risk = 0
        risk_reasons = []
        if has_diabetes and hba1c and hba1c > 9:
            high_risk = 1; risk_reasons.append("uncontrolled_diabetes")
        if has_hypertension and sbp1 and sbp1 > 160:
            high_risk = 1; risk_reasons.append("severe_hypertension")
        if has_tb and missed_doses and missed_doses > 5:
            high_risk = 1; risk_reasons.append("tb_treatment_default_risk")
        if has_tb and hiv:
            high_risk = 1; risk_reasons.append("tb_hiv_coinfection")
        if has_diabetes and has_hypertension:
            high_risk = 1; risk_reasons.append("cardiometabolic_comorbidity")

        patients.append({
            "patient_id":            pid,
            "domain":                "chronic",
            "patient_type":          "chronic_patient",
            "name":                  name,
            "age":                   age,
            "dob":                   dob,
            "gender":                gender,
            "district":              district,
            "village":               village,
            "taluk":                 taluk,
            "visit_date":            random_date(0, 90),
            "record_entry_date":     random_date(0, 120),
            # maternal — null
            "gravida":               None,
            "parity":                None,
            "lmp_date":              None,
            "edd":                   None,
            "gestational_age_weeks": None,
            "anc_visits_count":      None,
            "systolic_bp":           None,
            "diastolic_bp":          None,
            "weight_kg":             None,
            "haemoglobin_gdl":       None,
            "urine_albumin":         None,
            "oedema_present":        None,
            "pallor_present":        None,
            "blood_sugar_fasting":   None,
            "fundal_height_cm":      None,
            "tt_1_given":            None,
            "tt_2_given":            None,
            "ifa_tablets_given":     None,
            # child — null
            "child_age_months":      None,
            "weight_child_kg":       None,
            "height_cm":             None,
            "muac_cm":               None,
            "waz_score":             None,
            "haz_score":             None,
            "sam_status":            None,
            "haemoglobin_child":     None,
            "bcg_given":             None,
            "opv0_given":            None,
            "opv1_given":            None,
            "opv2_given":            None,
            "opv3_given":            None,
            "dpt1_given":            None,
            "dpt2_given":            None,
            "dpt3_given":            None,
            "hepatitis_b_given":     None,
            "measles_given":         None,
            "mmr_given":             None,
            "pentavalent_given":     None,
            "vitamin_a_given":       None,
            "ifa_child_given":       None,
            "deworming_given":       None,
            "developmental_milestone_met": None,
            # chronic fields
            "chronic_condition":     subtype,
            "fasting_blood_sugar":   fbs,
            "postprandial_blood_sugar": ppbs,
            "hba1c":                 hba1c,
            "random_blood_glucose":  rbg,
            "insulin_dependent":     insulin_dep,
            "diabetes_medication_adherence": dm_adhere,
            "bmi":                   bmi,
            "waist_circumference":   waist,
            "foot_examination_done": foot_exam,
            "eye_examination_done":  eye_exam,
            "creatinine":            creatinine,
            "urine_microalbumin":    microalb,
            "bp_systolic_reading1":  sbp1,
            "bp_systolic_reading2":  sbp2,
            "bp_diastolic_reading1": dbp1,
            "bp_diastolic_reading2": dbp2,
            "pulse_rate":            pulse,
            "hypertension_medication_adherence": htn_adhere,
            "medication_name":       med_name,
            "salt_intake_compliant": salt_comp,
            "physical_activity_compliant": phys_act,
            "fundoscopy_done":       fundoscopy,
            "ecg_done":              ecg,
            "potassium":             potassium,
            "sputum_smear_result":   sputum,
            "genexpert_result":      genexpert,
            "chest_xray_result":     xray,
            "treatment_category":    tx_cat,
            "treatment_phase":       tx_phase,
            "dots_provider":         dots_prov,
            "missed_doses_count":    missed_doses,
            "tb_weight_kg":          tb_weight,
            "side_effects_reported": side_effects,
            "hiv_coinfection":       hiv,
            "contact_tracing_done":  contact_tr,
            # labels
            "true_high_risk":        high_risk,
            "true_high_risk_reason": ",".join(risk_reasons) if risk_reasons else "none",
        })

    return patients


# ===================================================
# MULTI-SOURCE RECORD GENERATION
# Apply cadre-specific noise and missingness
# ===================================================

def make_source_records(patient, cadre):
    """
    Given a base patient dict and a cadre, return a
    noisy source record reflecting that cadre's accuracy
    and field coverage.
    """
    r = patient.copy()
    r["cadre"]           = cadre
    r["data_source"]     = cadre
    r["source_record_id"] = f"{cadre}_{patient['patient_id']}"

    domain = patient["domain"]

    # ── NAME TRANSLITERATION ──────────────────────
    if cadre == "ASHA" and random.random() < 0.40:
        r["name"] = transliterate_name(r["name"])
    elif cadre == "ANGANWADI" and random.random() < 0.25:
        r["name"] = transliterate_name(r["name"])

    # ── AGE RECORDING ERROR ───────────────────────
    if cadre == "ASHA" and random.random() < 0.30:
        r["age"] = r["age"] + random.choice([-2, -1, 1, 2])

    # ── VISIT DATE VARIATION ──────────────────────
    if random.random() < 0.20:
        orig = datetime.strptime(r["visit_date"], "%d-%m-%Y")
        offset = random.randint(-45, 45)
        r["visit_date"] = (orig + timedelta(days=offset)).strftime("%d-%m-%Y")

    # ─────────────────────────────────────────────
    # DOMAIN: MATERNAL
    # ─────────────────────────────────────────────
    if domain == "maternal":

        noise = {
            "ASHA":      {"hb": (0.35, 1.2), "bp": (0.30, 15), "bs": (0.30, 30), "anc": 0.30, "wt": (0.25, 3.5), "fh": (0.10, 2.5)},
            "ANM":       {"hb": (0.08, 0.4), "bp": (0.08, 4),  "bs": (0.08, 8),  "anc": 0.05, "wt": (0.05, 1.0), "fh": (0.05, 1.0)},
            "PHC":       {"hb": (0.02, 0.1), "bp": (0.02, 2),  "bs": (0.02, 3),  "anc": 0.01, "wt": (0.01, 0.5), "fh": (0.01, 0.5)},
            "ANGANWADI": {"hb": (0.00, 0.0), "bp": (0.00, 0),  "bs": (0.15, 20), "anc": 0.20, "wt": (0.20, 3.0), "fh": (0.00, 0.0)},
        }[cadre]

        if r["haemoglobin_gdl"] is not None:
            r["haemoglobin_gdl"] = add_noise(r["haemoglobin_gdl"], noise["hb"][1], 6.0, 14.5, noise["hb"][0])
        if r["systolic_bp"] is not None:
            r["systolic_bp"] = int(add_noise(r["systolic_bp"], noise["bp"][1], 80, 180, noise["bp"][0]))
        if r["blood_sugar_fasting"] is not None:
            r["blood_sugar_fasting"] = add_noise(r["blood_sugar_fasting"], noise["bs"][1], 55, 240, noise["bs"][0])
        if r["anc_visits_count"] is not None and random.random() < noise["anc"]:
            r["anc_visits_count"] = max(0, r["anc_visits_count"] + random.choice([-1, 1]))
        if r["weight_kg"] is not None:
            r["weight_kg"] = add_noise(r["weight_kg"], noise["wt"][1], 35, 100, noise["wt"][0])
        if r["fundal_height_cm"] is not None:
            r["fundal_height_cm"] = add_noise(r["fundal_height_cm"], noise["fh"][1], 10, 42, noise["fh"][0])

        # Anganwadi doesn't measure some maternal clinical fields
        if cadre == "ANGANWADI":
            r["haemoglobin_gdl"]   = None
            r["systolic_bp"]       = None
            r["diastolic_bp"]      = None
            r["fundal_height_cm"]  = None
            r["urine_albumin"]     = None

        # ASHA has limited lab access
        if cadre == "ASHA":
            r["fundal_height_cm"]  = maybe_null(r["fundal_height_cm"], cadre, "fundal_height_cm")
            r["haemoglobin_gdl"]   = maybe_null(r["haemoglobin_gdl"],  cadre, "haemoglobin_gdl")
            r["blood_sugar_fasting"] = maybe_null(r["blood_sugar_fasting"], cadre, "blood_sugar_fasting")

    # ─────────────────────────────────────────────
    # DOMAIN: CHILD
    # ─────────────────────────────────────────────
    elif domain == "child":

        child_age_months = patient.get("child_age_months", 0) or 0

        # Anganwadi only covers under-6 (72 months)
        if cadre == "ANGANWADI" and child_age_months > 72:
            return None   # Anganwadi doesn't track 6-12 year olds

        noise = {
            "ASHA":      {"wt": (0.30, 0.8), "ht": (0.20, 2.0), "muac": (0.20, 0.8)},
            "ANM":       {"wt": (0.10, 0.4), "ht": (0.10, 1.0), "muac": (0.10, 0.4)},
            "PHC":       {"wt": (0.02, 0.2), "ht": (0.02, 0.5), "muac": (0.02, 0.2)},
            "ANGANWADI": {"wt": (0.20, 0.6), "ht": (0.15, 1.5), "muac": (0.15, 0.5)},
        }[cadre]

        if r["weight_child_kg"] is not None:
            r["weight_child_kg"] = add_noise(r["weight_child_kg"], noise["wt"][1], 2.0, 60, noise["wt"][0])
        if r["height_cm"] is not None:
            r["height_cm"] = add_noise(r["height_cm"], noise["ht"][1], 44, 155, noise["ht"][0])
        if r["muac_cm"] is not None:
            r["muac_cm"] = add_noise(r["muac_cm"], noise["muac"][1], 9.0, 21, noise["muac"][0])

        # Immunization recording errors — ASHA undercounts, PHC most accurate
        imm_fields = ["bcg_given","opv0_given","opv1_given","opv2_given","opv3_given",
                       "dpt1_given","dpt2_given","dpt3_given","hepatitis_b_given",
                       "measles_given","mmr_given","pentavalent_given"]
        error_prob = {"ASHA": 0.15, "ANM": 0.05, "PHC": 0.01, "ANGANWADI": 0.10}[cadre]
        for f in imm_fields:
            if r[f] is not None:
                r[f] = flip_bool(r[f], error_prob)

        # Missingness
        r["haemoglobin_child"] = maybe_null(r["haemoglobin_child"], cadre, "haemoglobin_child")
        r["waz_score"]         = maybe_null(r["waz_score"],         cadre, "waz_score")
        r["haz_score"]         = maybe_null(r["haz_score"],         cadre, "haz_score")

        # Hepatitis B and Pentavalent — ASHA less likely to record
        if cadre == "ASHA":
            if random.random() < 0.30: r["hepatitis_b_given"] = None
            if random.random() < 0.30: r["pentavalent_given"] = None
            if random.random() < 0.20: r["mmr_given"]         = None

    # ─────────────────────────────────────────────
    # DOMAIN: CHRONIC
    # ─────────────────────────────────────────────
    elif domain == "chronic":

        # Anganwadi does NOT track chronic disease patients
        if cadre == "ANGANWADI":
            return None

        subtype = patient.get("chronic_condition", "")

        if "diabetes" in subtype:
            if r["fasting_blood_sugar"] is not None:
                noise_p = {"ASHA": 0.0, "ANM": 0.40, "PHC": 0.02}[cadre]
                noise_s = {"ASHA": 0.0, "ANM": 18,   "PHC": 4  }[cadre]
                r["fasting_blood_sugar"] = add_noise(r["fasting_blood_sugar"], noise_s, 80, 400, noise_p)
            if r["postprandial_blood_sugar"] is not None:
                noise_p = {"ASHA": 0.0, "ANM": 0.35, "PHC": 0.02}[cadre]
                noise_s = {"ASHA": 0.0, "ANM": 22,   "PHC": 5  }[cadre]
                r["postprandial_blood_sugar"] = add_noise(r["postprandial_blood_sugar"], noise_s, 100, 500, noise_p)
            # Apply missingness
            r["hba1c"]            = maybe_null(r["hba1c"],           cadre, "hba1c")
            r["creatinine"]       = maybe_null(r["creatinine"],      cadre, "creatinine")
            r["urine_microalbumin"] = maybe_null(r["urine_microalbumin"], cadre, "urine_microalbumin")
            r["foot_examination_done"] = maybe_null(r["foot_examination_done"], cadre, "foot_examination_done")
            r["eye_examination_done"]  = maybe_null(r["eye_examination_done"],  cadre, "eye_examination_done")
            if cadre == "ASHA":
                r["fasting_blood_sugar"]     = None
                r["postprandial_blood_sugar"] = None

        if "hypertension" in subtype:
            if r["bp_systolic_reading1"] is not None:
                noise_p = {"ASHA": 0.40, "ANM": 0.20, "PHC": 0.03}[cadre]
                noise_s = {"ASHA": 18,   "ANM": 8,    "PHC": 3   }[cadre]
                r["bp_systolic_reading1"] = int(add_noise(r["bp_systolic_reading1"], noise_s, 90, 210, noise_p))
                r["bp_systolic_reading2"] = int(add_noise(r["bp_systolic_reading2"], noise_s, 90, 210, noise_p))
                r["bp_diastolic_reading1"] = int(add_noise(r["bp_diastolic_reading1"], noise_s//2, 55, 135, noise_p))
                r["bp_diastolic_reading2"] = int(add_noise(r["bp_diastolic_reading2"], noise_s//2, 55, 135, noise_p))
            r["fundoscopy_done"] = maybe_null(r["fundoscopy_done"], cadre, "fundoscopy_done")
            r["ecg_done"]        = maybe_null(r["ecg_done"],        cadre, "ecg_done")
            r["potassium"]       = maybe_null(r["potassium"],       cadre, "potassium")
            r["creatinine"]      = maybe_null(r["creatinine"],      cadre, "creatinine")
            r["waist_circumference"] = maybe_null(r["waist_circumference"], cadre, "waist_circumference")

        if "tb" in subtype:
            r["genexpert_result"]   = maybe_null(r["genexpert_result"],   cadre, "genexpert_result")
            r["chest_xray_result"]  = maybe_null(r["chest_xray_result"],  cadre, "chest_xray_result")
            r["sputum_smear_result"] = maybe_null(r["sputum_smear_result"], cadre, "sputum_smear_result")
            r["hiv_coinfection"]    = maybe_null(r["hiv_coinfection"],    cadre, "hiv_coinfection")
            # Missed doses — ASHA and ANM may undercount
            if r["missed_doses_count"] is not None:
                if cadre == "ASHA" and random.random() < 0.30:
                    r["missed_doses_count"] = max(0, r["missed_doses_count"] + random.randint(-2, 3))
                elif cadre == "ANM" and random.random() < 0.10:
                    r["missed_doses_count"] = max(0, r["missed_doses_count"] + random.randint(-1, 2))

    return r


# ===================================================
# MAIN
# ===================================================

def generate_all():

    os.makedirs("data/synthetic", exist_ok=True)

    # Generate base patients
    maternal_patients = generate_maternal_patients()
    child_patients    = generate_child_patients()
    chronic_patients  = generate_chronic_patients()

    all_patients = maternal_patients + child_patients + chronic_patients

    print(f"\nTotal base patients: {len(all_patients):,}")

    # Generate multi-source records
    print("Generating multi-source records...")

    all_records = []

    cadres = ["ASHA", "ANM", "PHC", "ANGANWADI"]

    for patient in all_patients:
        for cadre in cadres:
            record = make_source_records(patient, cadre)
            if record is not None:   # None = cadre doesn't cover this patient
                all_records.append(record)

    df = pd.DataFrame(all_records)

    # ── SAVE UNIFIED FILE ────────────────────────
    df.to_csv(
        "data/synthetic/unified_health_records.csv",
        index=False
    )

    # ── SAVE PER-DOMAIN FILES ────────────────────
    for domain in ["maternal", "child", "chronic"]:
        domain_df = df[df["domain"] == domain]
        domain_df.to_csv(
            f"data/synthetic/{domain}_records.csv",
            index=False
        )

    # ── SAVE PER-CADRE FILES ─────────────────────
    for cadre in cadres:
        cadre_df = df[df["cadre"] == cadre]
        cadre_df.to_csv(
            f"data/synthetic/{cadre.lower()}_records.csv",
            index=False
        )

    # Keep backward compatibility — maternal_records.csv
    df[df["domain"] == "maternal"].to_csv(
        "data/synthetic/maternal_records.csv",
        index=False
    )

    # ── SUMMARY ──────────────────────────────────
    print("\nDataset Generated Successfully")
    print("=" * 60)

    print(f"\nPatient Counts:")
    print(f"  Maternal patients     : {len(maternal_patients):,}")
    print(f"  Child patients        : {len(child_patients):,}")
    print(f"  Chronic patients      : {len(chronic_patients):,}")
    print(f"  Total patients        : {len(all_patients):,}")
    print(f"  Total source records  : {len(df):,}")

    print(f"\nCadre Distribution:")
    print(df["cadre"].value_counts().to_string())

    print(f"\nDomain Distribution:")
    print(df["domain"].value_counts().to_string())

    print(f"\nChronic Subtype Distribution:")
    chronic_df = df[df["domain"] == "chronic"].drop_duplicates("patient_id")
    print(chronic_df["chronic_condition"].value_counts().to_string())

    print(f"\nHigh Risk by Domain:")
    for domain in ["maternal", "child", "chronic"]:
        d = df[df["domain"] == domain].drop_duplicates("patient_id")
        hr = d["true_high_risk"].sum()
        print(f"  {domain:<10}: {hr:,} / {len(d):,}  ({hr/len(d)*100:.1f}%)")

    print(f"\nDistricts Covered     : {df['district'].nunique()}")

    print(f"\nFiles Saved:")
    print(f"  data/synthetic/unified_health_records.csv")
    print(f"  data/synthetic/maternal_records.csv")
    print(f"  data/synthetic/child_records.csv")
    print(f"  data/synthetic/chronic_records.csv")
    print(f"  data/synthetic/asha_records.csv")
    print(f"  data/synthetic/anm_records.csv")
    print(f"  data/synthetic/phc_records.csv")
    print(f"  data/synthetic/anganwadi_records.csv")

    return df


if __name__ == "__main__":
    generate_all()