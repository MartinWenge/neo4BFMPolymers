from abc import ABC, abstractmethod
import re

class abstract_parser(ABC):
    def __init__(self, fn):
        self.filename = fn
        # empty regex for base class
        self.key_dict = {'line': re.compile(r'^$')}
        self.dataBlock_dict = {'line': re.compile(r'^$')}

    def _parse_line(self, line):
        """ Apply the regex key dictionary on every line to find key value pairs

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
        """ Apply the regex dictionary dataBlock_dict on every data block line to find key value pairs

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

    @abstractmethod
    def parse_file(self):
        pass
    #