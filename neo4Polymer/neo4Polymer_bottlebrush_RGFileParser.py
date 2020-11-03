import re
from .neo4Polymer_abstractParser import abstract_parser
import logging
import numpy as np


logger = logging.getLogger(__name__)


class neo4Polymer_bottlebrush_RgFileParser(abstract_parser):
    """ Read RgTensor files written by the LeMonADE's Analyzer-To-Be-Found for bottlebrushes.

    The parser defines a set of keys that can be found in the radius of gyration files.
    """
    def __init__(self, fn):
        """ Init function of the bottlebrush Rg file parser introducing read keys.

        Parameters:
            fn (str): name of the Rg file

        Returns:
            None
        """
        abstract_parser.__init__(self, fn)
        self.key_dict = {
            'number_of_monomers': re.compile(r'#[ \t]+Number of monomers:[ \t](?P<number_of_monomers>\d+)\n'),
            'feature_name': re.compile(r'# Feature(?P<feature_name>.*)\n'),
            'data_block': re.compile(r'# mcs[ \t]+R_G molecule[ \t]+R_G backbone[ \t]+R_G sidechains\n')
        }
        self.dataBlock_dict = {
            'line': re.compile(r'[\w\+\-\.]+[ \t]+(?P<rg_molecule>\d+\.\d+)[ \t]+(?P<rg_backbone>\d+\.\d+)[ \t]+(?P<rg_sidechain>\d+\.\d+)[ \t\n]+')
        }

    def parse_file(self):
        """Parse content of a given radius of gyration tensor file

        Parameters:
            filepath (str): path to the rg tensor file

        Returns:
            data (list): parsed data summarized

        """
        # create an empty list to collect the data
        data = []
        rg_data = []
        # open the file and read through it line by line
        with open(self.filename, 'r') as file_object:
            line = file_object.readline()
            counter = 0
            while line:
                # at each line check for a match with a regex
                key, match = self._parse_line(line)

                # check the total number of lines read in
                counter = counter + 1

                # matches with value on line
                if key == 'number_of_monomers':
                    data.append([key, match.group(key)])

                if key == 'feature_name':
                    data.append([key, "Feature" + str(match.group(key))])

                if key == 'data_block':
                    # next line empty? if not terminate here
                    data_block_line = file_object.readline()
                    if not data_block_line == "\n":
                        logger.debug("WARNING: data block of rg file is not formated as expected")
                        return False

                    while data_block_line:
                        # check for different molecule groups
                        data_block_line = file_object.readline()
                        db_key, db_match = self._parse_data_block(data_block_line)

                        if db_key == 'line':
                            rg_data.append([db_match.group("rg_molecule"), db_match.group("rg_backbone"), db_match.group("rg_sidechain")])

                    # after this block, the loop can stop, even if not the very last line of the file
                    line = False

                # read next line
                line = file_object.readline()

            # close the file safely as there might be many files
            file_object.close()

        # if rg_data is not empty, calculate the mean using numpy
        if rg_data:
            rg_np_array = np.array(rg_data, dtype=np.float32)

            if (rg_np_array.shape[0] > 60):
                startIdx = int(rg_np_array.shape[0] / 2)
            else:
                logger.debug("WARNING: Number of samples in RGFile parser less than 60 ({}), use 3/4 of all samples for the mean.".format(rg_np_array.size))
                startIdx = int(rg_np_array.shape[0] / 4)

            data.append(["molecule_rg", np.mean(rg_np_array[startIdx:, 0])])
            data.append(["backbone_rg", np.mean(rg_np_array[startIdx:, 1])])
            data.append(["sidechain_rg", np.mean(rg_np_array[startIdx:, 2])])

        return data
#
