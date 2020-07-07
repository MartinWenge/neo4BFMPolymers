import re

## ------------------------------------  #####  ------------------------------------ ##
## ------------------------------------  #####  ------------------------------------ ##
class neo4Polymer_BFM_fileparser:
    """ Python class to read BFM-file headers written by the LeMonADE tool AnalyzerWriteBFMFile.
    
    The parser defines a set of keys that can be found in the BFM files.
    """
    def __init__(self, fn):
        """ Init function function of BFM fileparser introducing the read keys for the file header.
        
        Parameters:
            fn (str): name of the BFM file
            
        Returns:
            None
        """
        self.filename = fn
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
        }
        
        
    def _parse_line(self,line):
        """ Apply the regex dictionary on every line to find key value pairs
        
        Parameters:
            line (str): the actual line of the file or a string
            
        Returns:
            key and value of the regex dictionary defined in rx_dict if something was found
            None, None otherwise
        """
        for key, rx in self.key_dict.items():
            match = rx.search(line)
            if match:
                return key, match.group(key)
        # if there are no matches
        return None, None


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
                # at each line check for a match with a regex
                key, match = self._parse_line(line)
                
                # check the total number of lines read in
                counter = counter + 1
                
                # find mcs to stop after header
                if key == 'mcs':
                    data.append([key,match])
                    print("reached mcs command, stop reading. last mcs= ", match)
                    # does this finish the loop?
                    line = False
                    # close file
    
                # matches with value on line
                if key == 'number_of_monomers':
                    data.append([key,match])
                    
                if key == 'box_x':
                    data.append([key,match])
                
                if key == 'box_y':
                    data.append([key,match])
                    
                if key == 'box_z':
                    data.append([key,match])
                    
                if key == 'periodic_x':
                    data.append([key,match])
                    
                if key == 'periodic_y':
                    data.append([key,match])
                
                if key == 'periodic_z':
                    data.append([key,match])
                
                if key == 'nn_interaction':
                    data.append([key,match])
                
                if key == 'feature_name':
                    data.append([key,"Feature"+match])

                # read next line
                line = file_object.readline()
            
            # close the file savely as there might be many files 
            file_object.close()
            
        return data
#
