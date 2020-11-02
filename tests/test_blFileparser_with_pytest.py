# add parent directory to the available modules
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
libdir = "{parent}/{lib}".format(parent=parentdir, lib="neo4Polymer")
sys.path.insert(0, libdir)
import neo4Polymer


def test_read_dendr_g4_s4_b64_solv_e05_bl():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = neo4Polymer.neo4Polymer_bondLengthFileParser("tests/dendr_g4_s4_b64_solv_e05_bl.dat")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIO'], ['feature_name', 'FeatureBox'],
    # ['feature_name', 'FeatureBondset<FastBondset>'], ['feature_name', 'FeatureAttributes'],
    # ['mean_bl', xxx]]

    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []

    # ##  ---- features ----  ## #
    search = "feature_name"
    result = [dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search]
    num_feature_entries = len(result)
    expected = 4
    if not (num_feature_entries == expected):
        errors.append("number of features is {} != {}".format(result, expected))
    expected = 'FeatureMoleculesIO'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBox'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBondset<FastBondset>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureAttributes<int>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))

    # ##  ---- num of monomers ----  ## #
    search = "number_of_monomers"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    # result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 181
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ---- squared  results ----  ## #
    search = "mean_bl"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 6.9235
    if not (abs(result - expected) < 0.0001):
        errors.append("mean_bl^2 is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))
#
