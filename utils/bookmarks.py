import os
import re
from typing import Dict

from pypdf import PdfReader

TAB_SIZE = 4


class PdfExtractor:
    def __init__(self, pdf, beg, end) -> None:
        self.beg = beg
        self.end = end
        self.reader = PdfReader(pdf)

    def bm_dict(self, bookmarks) -> Dict[str | int, str]:
        bm = {}
        for i in bookmarks:
            if isinstance(i, list):
                bm |= self.bm_dict(i)
            else:
                page = self.reader.get_destination_page_number(i)
                tit = i.title.replace('  ', ' ')
                bm[','.join([str(page), tit])] = tit
        return bm

    def __call__(self):
        bm = self.bm_dict(self.reader.outline)

        for k, v in bm.items():
            if self.beg == v:
                p_lo = int(k.split(',')[0])
            if self.end == v:
                p_hi = int(k.split(',')[0])
                break

        if p_hi == p_lo:
            txt = self.reader.pages[p_lo].extract_text()
        else:
            txt = [self.reader.pages[p].extract_text() for p in range(p_lo, p_hi + 1)]
            lo = next((i for i, x in enumerate(txt) if x.strip() == self.beg), -1)
            hi = next((i for i, x in enumerate(txt) if x.strip() == self.end), len(txt))
            txt = '\n'.join(txt[lo:hi])

        return txt


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

            self.toc = [i.replace('  ', ' ') for i in self.toc]
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
