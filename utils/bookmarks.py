import os
import re

TAB_SIZE = 4


class BookmarksExtractor:
    def __init__(
        self,
        pdf: str,
        temp_toc: str | None = 'temp.txt',
    ):
        if pdf:
            os.system(
                f'''
                pdfxmeta -a 1 {pdf} >> recipe.toml
                pdfxmeta -a 2 {pdf} >> recipe.toml
                pdftocgen {pdf} < recipe.toml > {temp_toc}
                '''
            )
        with open(temp_toc, 'r') as f:
            self.toc = [i.strip() for i in f.readlines()]

    def __call__(self, postprocess: bool = True):
        if postprocess:
            # start from toc string
            target = '目次'
            start = next((i for i, l in enumerate(self.toc) if target in l), 0)
            self.toc = self.toc[start:]

            # remove lines with '...'
            self.toc = [i for i in self.toc if '...' not in i]

            # find lines with number pattern
            pattern = re.compile(r'(?<=^.{1})\d+\.(\d+)?(.\d+)?(.\d+)?\s.*')
            self.toc = list(filter(pattern.search, self.toc))

            # level indent based on number pattern
            num = [i.strip()[1] for i in self.toc]
            level = [
                (len(i) - 1) if i[1].isnumeric() else 0
                for i in [l.split()[0].split('.') for l in self.toc]
            ]
            for i, l in enumerate(self.toc):
                if '目次' in l:
                    continue
                cur_lv = level[i]
                pre_lv = level[i - 1] if i > 0 else None
                pre = num[i - 1] if i > 0 else None
                cur = num[i]
                nex = num[i + 1] if i < len(self.toc) - 1 else None

                if pre and cur and nex and pre_lv and cur_lv < pre_lv and cur < nex:
                    level[i] = pre_lv
                    if cur < pre:
                        level[i] += 1

                self.toc[i] = level[i] * TAB_SIZE * ' ' + l

        return '\n'.join(self.toc)
