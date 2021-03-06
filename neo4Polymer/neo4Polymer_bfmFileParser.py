import re
from .neo4Polymer_abstractParser import abstract_parser
import logging


logger = logging.getLogger(__name__)


class neo4Polymer_BFM_fileparser(abstract_parser):
    """ Read BFM-file headers written by the LeMonADE's AnalyzerWriteBFMFile.

    The parser defines a set of keys that can be found in the BFM files.
    """
    def __init__(self, fn):
        """ Init function of BFM fileparser introducing read keys.

        Parameters:
            fn (str): name of the BFM file

        Returns:
            None
        """
        abstract_parser.__init__(self, fn)
        self.key_dict = {
            'mcs': re.compile(r'!mcs=(?P<mcs>\d+)\n'),
            'number_of_monomers': re.compile(r'!number_of_monomers=(?P<number_of_monomers>\d+)\n'),
            'box_x': re.compile(r'!box_x=(?P<box_x>\d+)\n'),
            'box_y': re.compile(r'!box_y=(?P<box_y>\d+)\n'),
            'box_z': re.compile(r'!box_z=(?P<box_z>\d+)\n'),
            'periodic_x': re.compile(r'!periodic_x=(?P<periodic_x>\d+)\n'),
            'periodic_y': re.compile(r'!periodic_y=(?P<periodic_y>\d+)\n'),
            'periodic_z': re.compile(r'!periodic_z=(?P<periodic_z>\d+)\n'),
            'nn_interaction': re.compile(r'!nn_interaction (\d) (\d) (?P<nn_interaction>\d+\.\d+)\n'),
            'feature_name': re.compile(r'# Feature(?P<feature_name>.*)\n'),
            'number_of_rings': re.compile(r'#!number_of_rings=(?P<number_of_rings>\d+)\n'),
            'number_of_monomers_per_ring': re.compile(r'#!number_of_monomers_per_ring=(?P<number_of_monomers_per_ring>\d+)\n'),
            'dendrimer_generation': re.compile(r'#!dendrimer_generation=(?P<dendrimer_generation>\d+)\n'),
            'dendrimer_spacer_length': re.compile(r'#!dendrimer_spacer_length=(?P<dendrimer_spacer_length>\d+)\n'),
            'dendrimer_core_functionality': re.compile(r'#!dendrimer_core_functionality=(?P<dendrimer_core_functionality>\d+)\n'),
            'dendrimer_branching_point_functionality': re.compile(r'#!dendrimer_branching_point_functionality=(?P<dendrimer_branching_point_functionality>\d+)\n'),
            'number_of_tendomers': re.compile(r'#!number_of_tendomers=(?P<number_of_tendomers>\d+)\n'),
            'number_of_crosslinkers': re.compile(r'#!number_of_crosslinkers=(?P<number_of_crosslinkers>\d+)\n'),
            'number_of_labels_per_arm': re.compile(r'#!number_of_labels_per_arm=(?P<number_of_labels_per_arm>\d+)\n'),
            'number_of_monomers_per_chain': re.compile(r'#!number_of_monomers_per_chain=(?P<number_of_monomers_per_chain>\d+)\n'),
            'spring_potential_constant': re.compile(r'#!spring_potential_constant=(?P<spring_potential_constant>[-+]?\d*\.\d+|\d+)\n'),
            'spring_potential_length': re.compile(r'#!spring_potential_length=(?P<spring_potential_length>\d+)\n'),
            'virtual_spring_constant': re.compile(r'#!virtual_spring_constant=(?P<virtual_spring_constant>[-+]?\d*\.\d+|\d+)\n'),
            'virtual_spring_length': re.compile(r'#!virtual_spring_length=(?P<virtual_spring_length>\d+)\n')
        }

    def parse_file(self):
        """Parse contant of a given bfm file

        Parameters:
            filepath (str): path to the bfm file

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
                # check the total number of lines read in
                counter = counter + 1

                # at each line check for a match with a regex
                key, reMatch = self._parse_line(line)

                if (reMatch is not None):
                    match = reMatch.group(key)

                    # find mcs to stop after header
                    if key == 'mcs':
                        data.append([key, match])
                        logger.info("reached mcs command, stop reading. last mcs= {}".format(match))
                        # does this finish the loop?
                        line = False
                        # close file

                    # matches with value on line
                    if key == 'number_of_monomers':
                        data.append([key, match])

                    if key == 'box_x':
                        data.append([key, match])

                    if key == 'box_y':
                        data.append([key, match])

                    if key == 'box_z':
                        data.append([key, match])

                    if key == 'periodic_x':
                        data.append([key, match])

                    if key == 'periodic_y':
                        data.append([key, match])

                    if key == 'periodic_z':
                        data.append([key, match])

                    if key == 'nn_interaction':
                        data.append([key, match])

                    if key == 'number_of_rings':
                        data.append([key, match])

                    if key == 'number_of_monomers_per_ring':
                        data.append([key, match])

                    if key == 'number_of_tendomers':
                        data.append([key, match])

                    if key == 'number_of_crosslinkers':
                        data.append([key, match])

                    if key == 'number_of_labels_per_arm':
                        data.append([key, match])

                    if key == 'number_of_monomers_per_chain':
                        data.append([key, match])

                    if key == 'dendrimer_generation':
                        data.append([key, match])

                    if key == 'dendrimer_spacer_length':
                        data.append([key, match])

                    if key == 'dendrimer_core_functionality':
                        data.append([key, match])

                    if key == 'dendrimer_branching_point_functionality':
                        data.append([key, match])

                    if key == 'spring_potential_constant':
                        data.append([key, match])

                    if key == 'spring_potential_length':
                        data.append([key, match])

                    if key == 'virtual_spring_constant':
                        data.append([key, match])

                    if key == 'virtual_spring_length':
                        data.append([key, match])

                    if key == 'feature_name':
                        data.append([key, "Feature" + match])

                # read next line
                line = file_object.readline()

            # close the file safely as there might be many files
            file_object.close()

        return data
#
