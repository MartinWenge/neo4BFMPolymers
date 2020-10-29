import re
import numpy as np
from .neo4Polymer_abstractParser import abstract_parser
import logging


logger = logging.getLogger(__name__)


class neo4Polymer_singleDendrimer_RgT_fileparser(abstract_parser):
    """ Read Rg files written by LeMonADE's Analyzer-To-Be-Found.

    The parser defines a set of keys that can be found in the radius of gyration tensor files.
    """
    def __init__(self, fn):
        """ Init function of Rg fileparser introducing read keys.

        Parameters:
            fn (str): name of the Rg file

        Returns:
            None
        """
        abstract_parser.__init__(self, fn)
        self.key_dict = {
            'moleculePart': re.compile(r'# Radius of Gyration Tensor of DendrimerRGTensorAnalyzer:[ \t]+(?P<moleculePart>([\w ]+))\n'),
            'data_block': re.compile(r'# time[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+([\w<>]+)\n')
        }
        self.dataBlock_dict = {
            'line': re.compile(r'(\d+?)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)\n')
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

                if key == 'moleculePart':
                    data.append([key, match.group(key)])

                if key == 'data_block':
                    data_block_line = line
                    while data_block_line:
                        data_block_line = file_object.readline()
                        db_key, db_match = self._parse_data_block(data_block_line)
                        if db_key == 'line':
                            # read of rg^2 and <A>
                            rg_data.append([db_match[5], db_match[8]])

                    # after this block, the loop can stop, even if not the very last line of the file
                    line = False

                # read next line
                line = file_object.readline()

            # close the file savely as there might be many files
            file_object.close()

        # if rg_data is not empty, calculate the mean using numpy
        if (len(rg_data) > 1):
            rg_np_array = np.array(rg_data, dtype=np.float32)
            if (rg_np_array.shape[0] > 100):
                startIdx = 80
            else:
                logger.debug("WARNING: Number of samples in RGFile parser less than 60 (", rg_np_array.size, "), use 3/4 of all samples for the mean.")
                startIdx = int(rg_np_array.shape[0] / 4)

            data.append(["mean_rg", np.mean(rg_np_array[startIdx, 0])])
            data.append(["mean_A", np.mean(rg_np_array[startIdx, 1])])

        return data
#
