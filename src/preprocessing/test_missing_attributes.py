from entity_resolution import composite_score


def test_missing_attribute_does_not_become_zero_score():

    row1 = {
        "domain": "maternal",
        "name": "Anita Sharma",
        "age": 30,
        "village": "Hassan",
        "gender": "Female",
        "dob": "1996-01-01",
    }

    row2 = {
        "domain": "maternal",
        "name": "Anita Sharma",
        "age": 30,
        "village": "Hassan",
        "gender": "Female",
        "dob": None,
    }

    score = composite_score(row1, row2)

    # Missing DOB should be ignored, not treated as a mismatch.
    assert score == 100.0


def test_multiple_missing_attributes_are_handled():

    row1 = {
        "domain": "maternal",
        "name": "Anita Sharma",
        "age": 30,
        "village": "Hassan",
        "gender": "Female",
        "dob": "1996-01-01",
    }

    row2 = {
        "domain": "maternal",
        "name": "Anita Sharma",
        "age": None,
        "village": None,
        "gender": "Female",
        "dob": None,
    }

    score = composite_score(row1, row2)

    # Name and gender remain available and are renormalized.
    assert score == 100.0


def test_all_matching_attributes_still_score_100():

    row1 = {
        "domain": "maternal",
        "name": "Anita Sharma",
        "age": 30,
        "village": "Hassan",
        "gender": "Female",
        "dob": "1996-01-01",
    }

    row2 = row1.copy()

    score = composite_score(row1, row2)

    assert score == 100.0

    