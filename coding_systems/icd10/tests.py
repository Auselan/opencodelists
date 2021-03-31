from coding_systems.icd10.coding_system import codes_by_type


def test_codes_by_type(icd10_data):
    assert codes_by_type(["A771", "M77", "M770", "M779"], None) == {
        "I: Certain infectious and parasitic diseases": ["A771"],
        "XIII: Diseases of the musculoskeletal system and connective tissue": [
            "M77",
            "M770",
            "M779",
        ],
    }
