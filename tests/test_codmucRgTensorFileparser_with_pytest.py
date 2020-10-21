# add parent directory to the available modules
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


import neo4Polymer_codmuc_RGTensorFileParser as rgTParser


def test_read_codmuc_micelle_g4_s4_m12_l4_e08_b128():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = rgTParser.neo4Polymer_cudmuc_RgTensor_fileparser("tests/codmuc_micelle_g4_s4_m12_l4_e0.8_b128_rg.dat")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIO'], ['feature_name', 'FeatureBox'],
    #  ['feature_name', 'FeatureBondset<FastBondset>'], ['feature_name', 'FeatureAttributes<int>'],
    #  ['number_of_monomers', '3324'],
    #  ['dendrimer_Rg2', '66.957847'], ['dendrimer_Rgx2', '22.233301'],
    #  ['dendrimer_Rgy2', '22.474591'], ['dendrimer_Rgz2', '22.249955'], ['dendrimer_<A>', '0.100552'],
    #  ['graftedChains_Rg2', '4.863455'], ['graftedChains_Rgx2', '1.620148'],
    #  ['graftedChains_Rgy2', '1.622357'], ['graftedChains_Rgz2', '1.620950'], ['graftedChains_<A>', '0.678891'],
    #  ['totalMolecule_Rg2', '110.308552'], ['totalMolecule_Rgx2', '36.630357'],
    #  ['totalMolecule_Rgy2', '36.967311'], ['totalMolecule_Rgz2', '36.710884'], ['totalMolecule_<A>', '0.072358']]

    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []
    print(data_array)
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
    expected = 3324
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ---- rg results dendrimer ----  ## #
    search = "dendrimer_Rg2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 66.957847
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_Rg2 is {} != {}".format(result, expected))

    search = "dendrimer_Rgx2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 22.233301
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_Rgx2 is {} != {}".format(result, expected))

    search = "dendrimer_Rgy2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 22.474591
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_Rgy2 is {} != {}".format(result, expected))

    search = "dendrimer_Rgz2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 22.249955
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_Rgz2 is {} != {}".format(result, expected))

    search = "dendrimer_<A>"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0.100552
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_<A> is {} != {}".format(result, expected))

    # ##  ---- rg results grafted chains ----  ## #
    search = "graftedChains_Rg2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 4.863455
    if not (abs(result - expected) < 0.00001):
        errors.append("graftedChains_Rg2 is {} != {}".format(result, expected))

    search = "graftedChains_Rgx2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1.620148
    if not (abs(result - expected) < 0.00001):
        errors.append("graftedChains_Rgx2 is {} != {}".format(result, expected))

    search = "graftedChains_Rgy2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1.622357
    if not (abs(result - expected) < 0.00001):
        errors.append("graftedChains_Rgy2 is {} != {}".format(result, expected))

    search = "graftedChains_Rgz2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 1.620950
    if not (abs(result - expected) < 0.00001):
        errors.append("graftedChains_Rgz2 is {} != {}".format(result, expected))

    search = "graftedChains_<A>"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0.678891
    if not (abs(result - expected) < 0.00001):
        errors.append("graftedChains_<A> is {} != {}".format(result, expected))

    # ##  ---- rg results total molecule ----  ## #
    search = "totalMolecule_Rg2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 110.308552
    if not (abs(result - expected) < 0.00001):
        errors.append("totalMolecule_Rg2 is {} != {}".format(result, expected))

    search = "totalMolecule_Rgx2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 36.630357
    if not (abs(result - expected) < 0.00001):
        errors.append("totalMolecule_Rgx2 is {} != {}".format(result, expected))

    search = "totalMolecule_Rgy2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 36.967311
    if not (abs(result - expected) < 0.00001):
        errors.append("totalMolecule_Rgy2 is {} != {}".format(result, expected))

    search = "totalMolecule_Rgz2"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 36.710884
    if not (abs(result - expected) < 0.00001):
        errors.append("totalMolecule_Rgz2 is {} != {}".format(result, expected))

    search = "totalMolecule_<A>"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0.072358
    if not (abs(result - expected) < 0.00001):
        errors.append("totalMolecule_<A> is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
#
