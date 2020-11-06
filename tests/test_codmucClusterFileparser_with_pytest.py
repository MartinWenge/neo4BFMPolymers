# add parent directory to the available modules
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
libdir = "{parent}/{lib}".format(parent=parentdir, lib="neo4Polymer")
sys.path.insert(0, libdir)
import numpy as np
import neo4Polymer


def test_read_codmuc_micelle_g4_s4_m12_l4_e08_b128_clustersl():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = neo4Polymer.neo4Polymer_codmuc_ClusterFileParser("tests/codmuc_micelle_g4_s4_m12_l4_e0.8_b128_clusters_t_277.dat")
    data_array = testreader.parse_file()
    # expected output:
    # [['feature_name', 'FeatureMoleculesIO'], ['feature_name', 'FeatureBox'],
    # ['feature_name', 'FeatureBondset<FastBondset>'], ['feature_name', 'FeatureAttributes<int>'],
    # ['feature_name', 'FeatureLatticePowerOfTwo<unsigned char>'], ['feature_name', 'FeatureBoltzmann'],
    # ['feature_name', 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<unsigned char> >'],
    # ['feature_name', 'FeatureNNInteractionSc<FeatureLatticePowerOfTwo>'],
    # ['clusters', [['cluster_size', 'frequency'],[xxx,xxx]]]]


    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []

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
    expected = 'FeatureBoltzmann'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureExcludedVolumeSc<FeatureLatticePowerOfTwo<unsigned char> >'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))
    expected = 'FeatureNNInteractionSc<FeatureLatticePowerOfTwo>'
    if not (expected in result):
        errors.append("feature is {} != {}".format(result, expected))

    # ##  ---- num of monomers ----  ## #
    search = "number_of_monomers"
    result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    # result = int([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 3324
    if not (result == expected):
        errors.append("number of monomers is {} != {}".format(result, expected))

    # ##  ----  results ----  ## #
    search = "clusters"
    result = ([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = ['cluster_size', 'frequency']
    if not expected == result[0]:
        errors.append("cluster distribution has incorrect header {} != {}".format(result, expected))
    expected = np.array([[1,0.08500438468284127],[2,0.9148786904413914],[4,0.0001169248757673195]], dtype=np.float32)
    if not (np.abs(np.array(result[1:],dtype=np.float32) - expected).sum() < 0.0001):
        errors.append("cluster distribution is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))
#
