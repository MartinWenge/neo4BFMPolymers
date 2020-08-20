import re


class neo4Polymer_cudmuc_RgTensor_fileparser:
    """ Read RgTensor files written by the LeMonADE's Analyzer-To-Be-Found.

    The parser defines a set of keys that can be found in the radius of gyration tensor files.
    """
    def __init__(self, fn):
        """ Init function of RgTensor fileparser introducing read keys.

        Parameters:
            fn (str): name of the RgTensor file

        Returns:
            None
        """
        self.filename = fn
        self.key_dict = {
            'number_of_monomers': re.compile(r'#[ \t]+Number of monomers:[ \t](?P<number_of_monomers>\d+)\n'),
            'feature_name': re.compile(r'# Feature(?P<feature_name>.*)\n'),
            'data_block': re.compile(r'# ID[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+(\w+)[ \t]+([\w<>]+)\n')
        }
        self.dataBlock_dict = {
            'dendrimer': re.compile(r'd_\d+[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t\n]+'),
            'graftedChains': re.compile(r'l_\d+[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t\n]+'),
            'totalMolecule': re.compile(r't_\d+[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t]+(\d+\.\d+)[ \t\n]+')
        }

    def _parse_line(self, line):
        """ Apply the regex dictionary on every line to find key value pairs

        Parameters:
            line (str): the actual line of the file or a string

        Returns:
            key and value of the regex dictionary defined in key_dict
                if something was found
            None, None otherwise
        """
        for key, rx in self.key_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None

    def _parse_data_block(self, line):
        """ Apply the regex dictionary on every data block line to find key value pairs

        Parameters:
            line (str): the actual line of the data block or a string

        Returns:
            key and full match of the regex dictionary defined in dataBlock_dict
                if something was found
            None, None otherwise
        """
        for key, rx in self.dataBlock_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None

    def parse_file(self):
        """Parse content of a given radius of gyration tensor file

        Parameters:
            filepath (str): path to the rg tensor file

        Returns:
            data (list): parsed data summarized

        """
        # create an empty list to collect the data
        data = []
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
                    data.append([key, "Feature" + match.group(key)])

                if key == 'data_block':
                    # next line empty? if not terminate here
                    data_block_line = file_object.readline()
                    if not data_block_line == "\n":
                        print("WARNING: data block of rg tensor file is not formated as expected")
                        return False

                    while data_block_line:
                        # check for different molecule groups
                        data_block_line = file_object.readline()
                        db_key, db_match = self._parse_data_block(data_block_line)

                        if db_key == 'dendrimer' or db_key == 'graftedChains' or db_key == 'totalMolecule':
                            data.append(["{}_{}".format(db_key, match[1]), db_match[1]])
                            data.append(["{}_{}".format(db_key, match[2]), db_match[2]])
                            data.append(["{}_{}".format(db_key, match[3]), db_match[3]])
                            data.append(["{}_{}".format(db_key, match[4]), db_match[4]])
                            data.append(["{}_{}".format(db_key, match[8]), db_match[8]])

                    # after this block, the loop can stop, even if not the very last line of the file
                    line = False

                # read next line
                line = file_object.readline()

            # close the file savely as there might be many files
            file_object.close()

        return data
#
