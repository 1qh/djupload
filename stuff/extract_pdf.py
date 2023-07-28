from typing import Dict

from pypdf import PdfReader


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


content = PdfExtractor(
    pdf='TM05_function_spec_Rev110_J_bookmarks.pdf',
    beg='3.2.3 動作仕様',
    end='3.2.4 バックアップ',
)()

with open('spec.txt', 'w') as f:
    f.write(content)
