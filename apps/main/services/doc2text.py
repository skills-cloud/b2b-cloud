from pathlib import Path

import docx2txt


def doc2text(filepath: Path) -> str:
    return docx2txt.process(filepath)
