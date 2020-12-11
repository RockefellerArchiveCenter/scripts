from os.path import join

from iiif_prep.preparer import Preparer

FIXTURES_FILEPATH = "fixtures"

source = FIXTURES_FILEPATH

expected_officers = ['Bates', 'Beard 2', 'Gilpatric', 'Beard 1']


def setup():
    # for d in [SOURCE_DIR]:
    #     if isdir(d):
    #         shutil.rmtree(d)
    # shutil.copytree(FIXTURES_FILEPATH, SOURCE_DIR)
    pass


def test_get_officers():
    """docstring for test_something"""
    officers_list = Preparer().get_officers(source)
    assert all(item in expected_officers for item in officers_list)


def test_determine_structure():
    """docstring for test_find_mezzanine"""
    preparer = Preparer()
    for officer_name, expected_structure in [
            ("Bates", "CURRENT"), ("Beard 1", "MICROFILM"), ("Gilpatric", "LEGACY")]:
        preparer.officer_path = join(source, officer_name)
        structure = preparer.determine_structure(officer_name)
        assert structure == expected_structure


def test_get_list_of_diaries():
    """docstring for test_get_list_of_diaries"""
    preparer = Preparer()
    for officer_name, structure, expected_diaries in [
            ("Bates", "CURRENT", ["RF_Bates-M_1948-1949"])]:
        preparer.officer_path = join(source, officer_name)
        preparer.structure = structure
        diaries = preparer.get_list_of_diaries()
        assert (sets(diaries) == set(expected_diaries))
