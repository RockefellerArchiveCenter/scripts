from os import listdir, mkdir
from os.path import join
from shutil import rmtree

from iiif_prep.preparer import Preparer

FIXTURES_FILEPATH = "fixtures"

TARGET_DIRECTORY = "target_directory"

source = FIXTURES_FILEPATH

expected_officers = ['Bates', 'Beard 2', 'Gilpatric', 'Beard 1']


def test_run_method():
    mkdir(TARGET_DIRECTORY)
    print("Testing run method...")
    Preparer().run(source, TARGET_DIRECTORY)
    assert len(listdir(TARGET_DIRECTORY)) == 9
    rmtree(TARGET_DIRECTORY)


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


def test_get_mezzanine_path():
    print("Getting paths to mezzanine TIFFs...")
    preparer = Preparer()
    for officer_name, structure, diaries, expected_paths in [
        ("Bates", preparer.CURRENT, ["RF_Bates-M_1948-1949"], ["fixtures/Bates/TIFFs/Master-Edited/RF_Bates-M_1948-1949"]), ("Beard 1", preparer.MICROFILM, [
            "rac_rfdiaries_12-2_beard_1925-1938_001", "rac_rfdiaries_12-2_beard_1925-1938_001a", "rac_rfdiaries_12-2_beard_1925-1938_001b", "rac_rfdiaries_12-2_beard_1925-1938_002"], [
            "fixtures/Beard 1/Beard-Roll_01-Tiff_files/rac_rfdiaries_12-2_beard_1925-1938_001", "fixtures/Beard 1/Beard-Roll_01-Tiff_files/rac_rfdiaries_12-2_beard_1925-1938_001a", "fixtures/Beard 1/Beard-Roll_01-Tiff_files/rac_rfdiaries_12-2_beard_1925-1938_001b", "fixtures/Beard 1/Beard-Roll_01-Tiff_files/rac_rfdiaries_12-2_beard_1925-1938_002"]), ("Gilpatric", preparer.LEGACY, [
                "Gilpatric_1949", "Gilpatric_1950"], [
                    "fixtures/Gilpatric/Gilpatric_1949/Master_Edited", "fixtures/Gilpatric/Gilpatric_1950/Master_Edited"])]:
        preparer.officer_path = join(source, officer_name)
        preparer.structure = structure
        mezzanine_paths = []
        for d in diaries:
            mezzanine_paths.append(preparer.get_mezzanine_path(d))
        assert (set(mezzanine_paths) == set(expected_paths))
