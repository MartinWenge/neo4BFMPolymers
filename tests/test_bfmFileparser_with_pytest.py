# add parent directory to the available modules
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


import neo4Polymer_bfmFileParser as bfmParser


def test_read_codmuc_micelle_g3_s4_m27_l4_e08_b128():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = bfmParser.neo4Polymer_BFM_fileparser("tests/codmuc_micelle_g3_s4_m27_l4_e0.8_b128_1425000000_lastconfig.bfm")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIO'], ['feature_name', 'FeatureBox'],
    #  ['feature_name', 'FeatureBondset<FastBondset>'], ['feature_name', 'FeatureAttributes<int>'],
    #  ['feature_name', 'FeatureLatticePowerOfTwo<unsigned char>'],
    #  ['feature_name', 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<unsigned char> >'],
    #  ['feature_name', 'FeatureNNInteractionSc<FeatureLatticePowerOfTwo>'], ['feature_name', 'FeatureBoltzmann'],
    #  ['number_of_monomers', '133367'], ['box_x', '128'], ['box_y', '128'], ['box_z', '128'],
    #  ['periodic_x', '1'], ['periodic_y', '1'], ['periodic_z', '1'],
    #  ['nn_interaction', '0.8'], ['nn_interaction', '0.8'],
    #  ['mcs', '1450000000']]

    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []

    # ##  ---- box size ----  ## #
    search = "box_x"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 128
    if not (result == expected):
        errors.append("box_x is {} != {}".format(result, expected))

    search = "box_y"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 128
    if not (result == expected):
        errors.append("box_y is {} != {}".format(result, expected))

    search = "box_z"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 128
    if not (result == expected):
        errors.append("box_z is {} != {}".format(result, expected))

    # ##  ---- periodicity ----  ## #
    search = "periodic_x"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1
    if not (result == expected):
        errors.append("periodic_x is {} != {}".format(result, expected))

    search = "periodic_y"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1
    if not (result == expected):
        errors.append("periodic_y is {} != {}".format(result, expected))

    search = "periodic_z"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1
    if not (result == expected):
        errors.append("periodic_z is {} != {}".format(result, expected))

    # ##  ---- features ----  ## #
    search = "feature_name"
    result = [dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search]
    num_feature_entries = len(result)
    expected = 8
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
    expected = 'FeatureLatticePowerOfTwo<unsigned char>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<unsigned char> >'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureNNInteractionSc<FeatureLatticePowerOfTwo>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBoltzmann'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))

    # ##  ---- num of monomers ----  ## #
    search = "number_of_monomers"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 133367
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ---- mcs command ----  ## #
    search = "mcs"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1450000000
    if not (result == expected):
        errors.append("mcs is {} != {}".format(result, expected))

    # ##  ---- nn_interaction ----  ## #
    search = "nn_interaction"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0.8
    if not ((result - expected) < 0.000001):
        errors.append("mcs is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
#
