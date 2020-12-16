from os.path import join

from iiif_prep.preparer import Preparer

FIXTURES_FILEPATH = "fixtures"

source = FIXTURES_FILEPATH

expected_officers = ['Bates', 'Beard 2', 'Gilpatric', 'Beard 1']


def test_run_method():
    print("Testing run method...")
    Preparer().run(source, ".")


def test_get_officers():
    print("Getting officers...")
    officers_list = Preparer().get_officers(source, ["Test Directory"])
    assert all(item in expected_officers for item in officers_list)


def test_determine_structure():
    print("Determining structure...")
    preparer = Preparer()
    for officer_name, expected_structure in [
            ("Bates", preparer.CURRENT),
            ("Beard 1", preparer.MICROFILM),
            ("Gilpatric", preparer.LEGACY)]:
        preparer.officer_path = join(source,
                                     officer_name)
        structure = preparer.determine_structure(officer_name)
        assert structure == expected_structure


def test_get_list_of_diaries():
    print("Getting diaries...")
    preparer = Preparer()
    for officer_name, structure, expected_diaries in [
        ("Bates", preparer.CURRENT, ["RF_Bates-M_1948-1949"]), ("Beard 1", preparer.MICROFILM, [
            "rac_rfdiaries_12-2_beard_1925-1938_001", "rac_rfdiaries_12-2_beard_1925-1938_001a", "rac_rfdiaries_12-2_beard_1925-1938_001b", "rac_rfdiaries_12-2_beard_1925-1938_002"]), ("Gilpatric", preparer.LEGACY, [
            "Gilpatric_1949", "Gilpatric_1950"])]:
        preparer.officer_path = join(source, officer_name)
        preparer.structure = structure
        diaries = preparer.get_list_of_diaries()
        assert (set(diaries) == set(expected_diaries))

def test_get_mezzanine():
    """docstring for test_get_mezzanine"""
    pass