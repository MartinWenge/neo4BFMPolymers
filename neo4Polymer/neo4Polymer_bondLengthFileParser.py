import re
import numpy as np
from .neo4Polymer_abstractParser import abstract_parser
import logging


logger = logging.getLogger(__name__)


class neo4Polymer_bondLengthFileParser(abstract_parser):
    """ Read Bond length files written by LeMonADE's AnalyzerBondLength.

    The parser defines a set of keys that can be found in the bond length files.
    """
    def __init__(self, fn):
        """ Init function of bond length fileparser introducing read keys.

        Parameters:
            fn (str): name of the bond length file

        Returns:
            None
        """
        abstract_parser.__init__(self, fn)
        self.key_dict = {
            'number_of_monomers': re.compile(r'#[ \t]+Number of monomers:[ \t](?P<number_of_monomers>\d+)\n'),
            'feature_name': re.compile(r'# Feature(?P<feature_name>.*)\n'),
            'data_block': re.compile(r'# mcs[ \t]+BL frame[ \t]+BL averaged\n')
            # mcs	BL frame 	BL averaged
        }
        self.dataBlock_dict = {
            'line': re.compile(r'[\w\+\-\.]+[ \t]+(?P<bl_frame>\d+\.\d+)[ \t]+(?P<bl_average>\d+\.\d+)[ \t\n]+')
        }

    def parse_file(self):
        """Parse content of a given bond length file

        Parameters:
            filepath (str): path to the bond length file

        Returns:
            data (list): parsed data summarized

        """
        # create an empty list to collect the data
        data = []
        bl_data = []
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
                        logger.debug("WARNING: data block of bond length file is not formated as expected")
                        return False

                    while data_block_line:
                        # check for different molecule groups
                        data_block_line = file_object.readline()
                        db_key, db_match = self._parse_data_block(data_block_line)
                        if db_key == 'line':
                            # get frame bl to calculate average here
                            bl_data.append(np.float32(db_match.group('bl_frame')))

                    # after this block, the loop can stop, even if not the very last line of the file
                    line = False

                # read next line
                line = file_object.readline()

            # close the file safely as there might be many files
            file_object.close()

        # if bl_data is not empty, calculate the mean using numpy
        if (len(bl_data) > 1):
            bl_np_data = np.array(bl_data, dtype=np.float32)
            if (bl_np_data.size > 100):
                startIdx = int(bl_np_data.size / 2)
            else:
                logger.debug("WARNING: Number of samples in RGFile parser less than 60 ({}), use 3/4 of all samples for the mean.".format(bl_np_data.size))
                startIdx = int(bl_np_data.size / 4)
            data.append(["mean_bl", np.mean(bl_np_data[startIdx:])])

        return data
#
