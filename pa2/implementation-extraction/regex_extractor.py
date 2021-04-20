import re


class RegexExtractor:
    def __init__(self,
                 file_name: str,
                 single: dict = None,
                 multiple: dict = None,
                 multiple_title: str = None,
                 cleanup_content: bool = False) -> None:
        try:
            f = open(file_name, 'r', encoding='utf-8')
            self.contents = f.read()
        except UnicodeDecodeError:
            f = open(file_name, 'r')
            self.contents = f.read()

        # stores a dict where keys are data items;
        # values are arrays [regex, bool] where bool determines if re.DOTALL is used
        self.single = single
        self.multiple_title = multiple_title  # this will be used as a key for the next dict
        # stores a dict like single, except there are multiple iterations of it;
        # values are arrays [regex, bool] where bool determines if re.DOTALL is used
        self.multiple = multiple
        self.extracted = {}  # stores the extracted values
        self.cleanup_content = cleanup_content

    def find(self, needle: str, dot: bool) -> list:
        """
        A helper function that will interpret the haystack '.' symbol with newline or not.
        :param needle: the regex expression
        :param dot: does the . symbol represent new lines too?
        :return: list of results
        """
        if dot:
            return re.findall(needle, self.contents, re.DOTALL)
        return re.findall(needle, self.contents)

    def content_cleanup(self) -> None:
        """
        Cleanup the Content item in the extracted data and update it in the dict.
        """
        re_content = re.sub('<iframe[^>]*>.*?</iframe>', '', self.extracted['Content'])
        re_content = re.sub('<figure[^>]*>.*?</figure>', '', re_content, flags=re.DOTALL)
        re_content = re.sub('<div class="gallery">.*</div>', '', re_content, flags=re.DOTALL)
        re_content = re.sub('<p[^>]*>', '', re_content)
        re_content = re.sub('</p>', '\n', re_content)
        re_content = re.sub('<strong>', '', re_content)
        re_content = re.sub('</strong>', '', re_content)
        # re_content = re.sub('<br>', '\n', re_content)
        re_content = re.sub('<sub>', '', re_content)
        re_content = re.sub('</sub>', '', re_content)
        self.extracted['Content'] = re_content.strip()
        self.replace_br('Content')

    def replace_br(self, dict_item: str) -> None:
        """
        Replaces <br> tags with \n from an item in the extracted data.
        :param dict_item: The key of the field in the extracted data in which to perform replacements
        """
        self.extracted[dict_item] = re.sub('<br/?>', '\n', self.extracted[dict_item])

    def extract(self) -> dict:
        """
        Extracts data from the HTML file using the given regex expressions
        :return: JSON formed dict of extracted data
        """
        if not self.extracted:  # if extraction was not performed yet
            # extract values that appear only once
            if self.single:
                for key, val in self.single.items():
                    result = self.find(val[0], val[1])
                    if len(result) == 0:
                        result.append("")
                    self.extracted[key] = result[0]
            # extract values that appear multiple times
            if self.multiple:
                tmp_extracted = {}
                tmp_len = 0
                multiple_extracted = []
                # get the results for each data item
                for key, val in self.multiple.items():
                    current = self.find(val[0], val[1])
                    tmp_extracted[key] = current
                    tmp_len = len(current)
                # this goes from 0...amount of extracted data items
                for i in range(tmp_len):
                    tmp_dict = {}
                    # copy each i-th data item to tmp_dict
                    for k, v in tmp_extracted.items():
                        tmp_dict[k] = v[i]
                    multiple_extracted.append(tmp_dict)
                if self.multiple_title is None:
                    self.extracted['Items'] = multiple_extracted
                else:
                    self.extracted[self.multiple_title] = multiple_extracted
            if self.cleanup_content:
                self.content_cleanup()
        return self.extracted
