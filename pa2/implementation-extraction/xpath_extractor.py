from lxml import html
import elementpath


class XPathExtractor:
    JOIN_NONE: int = 0
    JOIN_ALL: int = 1
    JOIN_TWO: int = 2
    FORCE_LXML = 3

    def __init__(self, file_name: str, single: dict = None, multiple: dict = None, multiple_title: str = None) -> None:
        try:
            f = open(file_name, 'r')
            contents = f.read()
            self.tree = html.fromstring(contents)
        except UnicodeDecodeError:
            f = open(file_name, 'r', encoding='utf-8')
            contents = f.read()
            self.tree = html.fromstring(contents)

        self.single = single  # stores a dict where keys are data items; values are the XPath queries
        self.multiple_title = multiple_title  # this will be used as a key for the next dict
        self.multiple = multiple  # stores a dict like single, except there are multiple iterations of it
        self.extracted = {}  # stores the extracted values

    def joiner(self, result: list, how: int = 0, i: int = 0) -> str:
        """
        A helper function that resturns properly formatted content.
        :param result: the result of an XPath query
        :param how: constant on how the data should be joined/formatted
        :param i: if how==JOIN_TWO, add the index where the data should be joined
        :return: Properly formatted string with the extracted data
        """
        if how == self.JOIN_NONE:
            return result[i].strip()
        elif how == self.JOIN_ALL:
            tmp = ' '.join(result)
            return ' '.join(tmp.split())
        else:
            return result[2*i]+' '+result[2*i + 1]

    def extract(self) -> dict:
        """
        Extracts data from the HTML file using the given regex expressions
        :return: JSON formed dict of extracted data
        """
        if not self.extracted:  # if extraction was not performed yet
            # extract values that appear only once
            if self.single:
                for key, val in self.single.items():
                    if isinstance(val, list):
                        if val[1] == self.FORCE_LXML:
                            self.extracted[key] = self.joiner(self.tree.xpath(val[0]))
                        else:
                            self.extracted[key] = (self.joiner(elementpath.select(self.tree, val[0]), val[1]))
                    else:
                        self.extracted[key] = self.joiner(elementpath.select(self.tree, val))
            # extract values that appear multiple times
            if self.multiple:
                tmp_extracted = {}
                tmp_len = 0
                multiple_extracted = []
                # get the results for each data item
                for key, val in self.multiple.items():
                    if isinstance(val, list):
                        if val[1] == self.FORCE_LXML:
                            current = self.tree.xpath(val[0])
                        else:
                            current = (elementpath.select(self.tree, val[0]), val[1])
                    else:
                        current = elementpath.select(self.tree, val)
                        tmp_len = len(current)
                    tmp_extracted[key] = current
                # this goes from 0...amount of extracted data items
                for i in range(tmp_len):
                    tmp_dict = {}
                    # copy each i-th data item to tmp_dict
                    for k, v in tmp_extracted.items():
                        if isinstance(v, tuple):
                            tmp_dict[k] = self.joiner(v[0], v[1], i)
                        else:
                            tmp_dict[k] = self.joiner(v, i=i)
                    multiple_extracted.append(tmp_dict)
                if self.multiple_title is None:
                    self.extracted['Items'] = multiple_extracted
                else:
                    self.extracted[self.multiple_title] = multiple_extracted
        return self.extracted
