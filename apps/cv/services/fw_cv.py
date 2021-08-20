import datetime
import enum
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from main.services.doc2text import doc2text
from cv import models as cv_models

logger = logging.getLogger(__name__)


@dataclass
class FwCvExperience:
    date_from: datetime.date
    date_to: Optional[datetime.date]
    position_title: str
    organization_title: str
    text: str


@dataclass
class FwCvEducation:
    date: str
    title: str
    text: str


@dataclass
class FwCvCertificate(FwCvEducation):
    pass


@dataclass
class FwCvCompetency:
    title: str


@dataclass
class FwCv:
    gender: str
    age: Optional[int]
    city: Optional[str]
    citizenship: Optional[str]
    cv_title: str
    type_of_employment: List[str]
    experience: List[FwCvExperience]
    competencies: List[FwCvCompetency]


months_nums = {
    'январь': 1,
    'февраль': 2,
    'март': 3,
    'апрель': 4,
    'май': 5,
    'июнь': 6,
    'июль': 7,
    'август': 8,
    'сентябрь': 9,
    'октябрь': 10,
    'ноябрь': 11,
    'декабрь': 12,
}


def parse_fw_cv_text(cv_text: str) -> FwCv:
    cv_text_lines = cv_text.split('\n')

    gender_age = cv_text_lines[0].split(',')
    age = None
    gender = gender_age[0]
    if len(gender_age) > 1:
        age = int(re.sub(r'[^0-9]', '', gender_age[1]))
    logger.debug(f'gender:\t{gender}')
    logger.debug(f'age:\t{age}')

    city_re = re.compile(r'^Проживает: (.+)$', re.MULTILINE)
    city = None
    if city_search := city_re.search(cv_text):
        city = city_search.group(1)
    logger.debug(f'city:\t{city}')

    citizenship_re = re.compile(r'^Гражданство: (.+)$', re.MULTILINE)
    citizenship = None
    if citizenship_search := citizenship_re.search(cv_text):
        citizenship = citizenship_search.group(1)
    logger.debug(f'citizenship:\t{citizenship}')

    cv_title_re = re.compile(r'^Желаемая должность и зарплата\n\n(.+)$', re.MULTILINE)
    cv_title = None
    if cv_title_search := cv_title_re.search(cv_text):
        cv_title = cv_title_search.group(1)
    logger.debug(f'citizenship:\t{cv_title}')

    experience_re = re.compile(r'Опыт работы(.+)Образование\n', re.MULTILINE | re.DOTALL)
    experience = None
    if experience_search := experience_re.search(cv_text):
        experience = '\n'.join(experience_search.group(1).split('\n')[2:])
    logger.debug(f'experience:\t{experience}')


def parse_fw_cv_docx(filepath: Path) -> FwCv:
    return parse_fw_cv_text(doc2text(Path(filepath)))


def import_fw_cv_file_docx(filepath: Path) -> cv_models.CV:
    logger.info('import FW .docx', extra={'path': filepath})
    fw_cv = parse_fw_cv_docx(filepath)


def import_fw_cv_file_txt(filepath: Path) -> cv_models.CV:
    logger.info('import FW .txt', extra={'path': filepath})
    fw_cv = parse_fw_cv_text(filepath.read_text())
