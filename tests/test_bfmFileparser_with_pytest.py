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


def test_read_codmuc_micelle_g3_s4_m27_l4_e08_b128():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = neo4Polymer.neo4Polymer_BFM_fileparser("tests/codmuc_micelle_g3_s4_m27_l4_e0.8_b128_1425000000_lastconfig.bfm")
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


def test_read_RingMelt_N128_Phi05_Box128_EA5_EB17_MCS0_GPU():

    testreader = neo4Polymer.neo4Polymer_BFM_fileparser("tests/RingMelt_N128_Phi05_Box128_EA5_EB17_MCS0_GPU.bfm")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIOUnsaveCheck'], ['feature_name', 'FeatureBox'],
    # ['feature_name', 'FeatureBondsetUnsaveCheck<FastBondset>'], ['feature_name', 'FeatureAttributes<int>'],
    # ['feature_name', 'FeatureLatticePowerOfTwo<bool>'],
    # ['feature_name', 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<bool> >'],
    # ['feature_name', 'FeatureReactiveBonds'], ['feature_name', 'FeatureBreak'],
    # ['feature_name', 'FeatureConnectionSc'], ['feature_name', 'FeatureActivationEnergy'],
    # ['feature_name', 'FeatureBondEnergy'], ['feature_name', 'FeatureBoltzmann'],
    # ['feature_name', 'FeatureSystemInformationRingMelt'], ['number_of_monomers', '131072'],
    # ['box_x', '128'], ['box_y', '128'], ['box_z', '128'],
    # ['periodic_x', '1'], ['periodic_y', '1'], ['periodic_z', '1'],
    # ['number_of_rings', '1024'], ['number_of_monomers_per_ring', '128'], ['mcs', '0']]

    # still NOT supported:
    # #!activation_energy=5
    # #!breaking_energy=17

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
    expected = 13
    if not (num_feature_entries == expected):
        errors.append("number of features is {} != {}".format(result, expected))
    expected = 'FeatureMoleculesIOUnsaveCheck'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBox'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBondsetUnsaveCheck<FastBondset>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureAttributes<int>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureLatticePowerOfTwo<bool>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<bool> >'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBoltzmann'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureReactiveBonds'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBreak'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureConnectionSc'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureActivationEnergy'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBondEnergy'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureSystemInformationRingMelt'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))

    # ##  ---- num of monomers ----  ## #
    search = "number_of_monomers"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 131072
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ---- mcs command ----  ## #
    search = "mcs"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0
    if not (result == expected):
        errors.append("mcs is {} != {}".format(result, expected))

    # ##  ---- num of rings ----  ## #
    search = "number_of_rings"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1024
    if not (result == expected):
        errors.append("number of rings is {} != {}".format(result, expected))

    # ##  ---- num of monomers per ring ----  ## #
    search = "number_of_monomers_per_ring"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 128
    if not (result == expected):
        errors.append("number of monomers per ring is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))
#


def test_read_dend_chain_spring_g3_s4_l32_b64_d05_r012_k1():
    testreader = neo4Polymer.neo4Polymer_BFM_fileparser("tests/dend_chain_spring_g3_s4_l32_b64_d05_r012_k1.0.bfm")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIO'], ['feature_name', 'FeatureBox'],
    # ['feature_name', 'FeatureBondset<FastBondset>'], ['feature_name', 'FeatureVirtualSpringTwoObjects'],
    # ['feature_name', 'FeatureAttributes<int>'], ['feature_name', 'FeatureBoltzmann'],
    # ['feature_name', 'FeatureSystemInformationDendrimer'],
    # ['number_of_monomers', '16373'], ['box_x', '64'], ['box_y', '64'], ['box_z', '64'],
    # ['periodic_x', '1'], ['periodic_y', '1'], ['periodic_z', '1'],
    # ['virtual_spring_constant', '1'], ['virtual_spring_length', '12'], ['mcs', '0']]

    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []
    # breakpoint()

    # ##  ---- box size ----  ## #
    search = "box_x"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 64
    if not (result == expected):
        errors.append("box_x is {} != {}".format(result, expected))

    search = "box_y"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 64
    if not (result == expected):
        errors.append("box_y is {} != {}".format(result, expected))

    search = "box_z"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 64
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
    expected = 9
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
    expected = 'FeatureLatticePowerOfTwo<bool>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<bool> >'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureBoltzmann'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureSystemInformationDendrimer'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureVirtualSpringTwoObjects'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))

    # ##  ---- num of monomers ----  ## #
    search = "number_of_monomers"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 16373
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ---- mcs command ----  ## #
    search = "mcs"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0
    if not (result == expected):
        errors.append("mcs is {} != {}".format(result, expected))

    # ##  ---- spring constant ----  ## #
    search = "virtual_spring_constant"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1.0
    if not (result == expected):
        errors.append("spring constant {} != {}".format(result, expected))

    # ##  ---- spring length ----  ## #
    search = "virtual_spring_length"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 12
    if not (result == expected):
        errors.append("spring length {} != {}".format(result, expected))

    # ##  ---- generation ----  ## #
    search = "dendrimer_generation"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 3
    if not (result == expected):
        errors.append("generation {} != {}".format(result, expected))

    # ##  ---- spacer length ----  ## #
    search = "dendrimer_spacer_length"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 4
    if not (result == expected):
        errors.append("spacer length {} != {}".format(result, expected))

    # ##  ---- core functionality ----  ## #
    search = "dendrimer_core_functionality"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 3
    if not (result == expected):
        errors.append("core functionality {} != {}".format(result, expected))

    # ##  ---- branching point functionality ----  ## #
    search = "dendrimer_branching_point_functionality"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 3
    if not (result == expected):
        errors.append("branching point functionality {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))
#
