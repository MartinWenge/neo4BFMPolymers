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


def test_read_dendr_g4_s4_b64_solv_e05():
    # tell me, where we are ...
    # cwd = os.getcwd()
    # the_ls = os.listdir()
    # print(cwd, the_ls)

    testreader = neo4Polymer.neo4Polymer_singleDendrimer_RgT_fileparser("tests/dendr_g4_s4_b64_solv_e05_rg_mol.dat")
    data_array = testreader.parse_file()
    # expected output:
    # [['moleculePart', 'whole Molecule with endgroups'],
    # ['mean_rg', 148.376], ['mean_A', 0.141802]]

    # perform various test in a single function with an error array
    # https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []

    # ##  ---- moleculePart ----  ## #
    search = "moleculePart"
    result = ([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 'whole Molecule with endgroups'
    if not (result == expected):
        errors.append("molecule part {} != {}".format(result, expected))

    # ##  ---- rg results dendrimer ----  ## #
    search = "mean_rg"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 148.376
    if not (abs(result - expected) < 0.00001):
        errors.append("mean rg is {} != {}".format(result, expected))

    search = "mean_A"
    result = float([dataArrayElement[1] for dataArrayElement in data_array if dataArrayElement[0] == search][0])
    expected = 0.141802
    if not (abs(result - expected) < 0.00001):
        errors.append("dendrimer_Rgx2 is {} != {}".format(result, expected))

    # assert no error message has been registered, else print messages
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))
#
