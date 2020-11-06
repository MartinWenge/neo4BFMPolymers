import re
import numpy as np
from .neo4Polymer_abstractParser import abstract_parser
import logging


logger = logging.getLogger(__name__)


class neo4Polymer_codmuc_ClusterFileParser(abstract_parser):
    """ Read Cluster files written by LeMonADE's AnalyzerCluster.

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
            'data_block': re.compile(r'# Distribution of cluster sizes of molecules for copolymers.*\n')
        }
        self.dataBlock_dict = {
            'line': re.compile(r'#[ \t]+(?P<cluster_size>\d+)[ \t]+(?P<cluster_counts>\d+)\n'),
            'number_of_monomers_per_molecule': re.compile(r'#[ \t]+n[ \t]+H\(t_(?P<number_of_monomers_per_molecule>\d+)\)\n'),
            'terminate': re.compile(r'# [ \t]+t_(?P<number_of_monomers_per_molecule>\d+): num molecules n =.*\n')
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
        cluster_data = []
        num_monos_per_molecule = None
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
                    # next line header 2? if not terminate here
                    data_block_line = file_object.readline()
                    if not data_block_line == "# (XX): XX= key of respective molecule\n":
                        logger.debug("WARNING: data block of codmuc cluster file is not formated as expected")
                        return False

                    while data_block_line:
                        # check for different molecule groups
                        data_block_line = file_object.readline()
                        db_key, db_match = self._parse_data_block(data_block_line)
                        if db_key == 'number_of_monomers_per_molecule':
                            # get num of monomers per molecule
                            if num_monos_per_molecule is None:
                                num_monos_per_molecule = int(db_match.group(db_key))
                        if db_key == 'line':
                            # get size and counts here
                            cluster_data.append([db_match.group('cluster_size'),db_match.group('cluster_counts')])
                        if db_key == 'terminate':
                            # stop reading before detailed cluster information occurres
                            data_block_line = False
                            line = False

                    # after this block, the loop can stop anyway, even if not the very last line of the file
                    line = False

                # read next line
                line = file_object.readline()

            # close the file safely as there might be many files
            file_object.close()

        # if cluster_data is not empty, calculate the frequency
        if (len(cluster_data) > 1):
            cluster_np_data = np.array(cluster_data, dtype=np.float32)
            cluster_np_data[:,1] = cluster_np_data[:,1] / np.sum(cluster_np_data[:,1])
            data_list = cluster_np_data.tolist()
            data_list.insert(0,['cluster_size', 'frequency'])
            data.append(["clusters", data_list])

        return data
#
