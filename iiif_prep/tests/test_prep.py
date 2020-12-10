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
    bates_structure = Preparer().determine_structure(join(source, "Bates"), "Bates")
    beard_structure = Preparer().determine_structure(
        join(source, "Beard 1"), "Beard 1")
    gilpatric_structure = Preparer().determine_structure(
        join(source, "Gilpatric"), "Gilpatric")
    assert bates_structure == 'CURRENT'
    assert beard_structure == 'MICROFILM'
    assert gilpatric_structure == 'LEGACY'


def test_get_list_of_diaries():
    """docstring for test_get_list_of_diaries"""
    bates_list_expected = ["RF_Bates-M_1948-1949"]
    bates_list = Preparer().get_list_of_diaries(join(source, "Bates"), "CURRENT")
    beard_1_list_expected = ["rac_rfdiaries_12-2_beard_1925-1938_001", "rac_rfdiaries_12-2_beard_1925-1938_001a", "rac_rfdiaries_12-2_beard_1925-1938_001b", "rac_rfdiaries_12-2_beard_1925-1938_002"]
    beard_1_list = Preparer().get_list_of_diaries(join(source, "Beard 1"), "MICROFILM")
    gilpatric_list_expected = ["Gilpatric_1949", "Gilpatric_1950"]
    gilpatric_list = Preparer().get_list_of_diaries(join(source, "Gilpatric"), "LEGACY")
    assert bates_list_expected == bates_list
    assert sorted(beard_1_list_expected) == sorted(beard_1_list)
    assert sorted(gilpatric_list_expected) == sorted(gilpatric_list)
