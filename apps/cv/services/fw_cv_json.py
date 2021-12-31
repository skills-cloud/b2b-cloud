import datetime
from typing import List, Optional, Dict
import re
import logging
import ujson as json
from pathlib import Path
from transliterate import translit
from dateutil.parser import parse as date_parse

from main import models as main_models
from dictionary import models as dictionary_models

from cv import models as cv_models

logger = logging.getLogger(__name__)


class ImportFwCvJson:
    filepath: Path
    skip_exists: bool
    without_skills: bool
    rows: List[Dict]
    rows_len: int

    idents: Dict[str, int] = {}

    countries: Dict[str, dictionary_models.Country] = {}
    cities: Dict[str, dictionary_models.City] = {}
    contact_types: Dict[str, dictionary_models.ContactType] = {}
    competencies: Dict[str, dictionary_models.Competence] = {}
    organizations: Dict[str, main_models.Organization] = {}
    education_places: Dict[str, dictionary_models.EducationPlace] = {}
    education_specialities: Dict[str, dictionary_models.EducationSpecialty] = {}

    def __init__(self, filepath: Path, without_skills: bool = False, skip_exists: bool = False):
        self.filepath = filepath
        self.without_skills = without_skills
        self.skip_exists = skip_exists

    def do_import(self) -> None:
        logger.info('import FW .json', extra={'path': self.filepath})
        self.rows = json.load(self.filepath.open())
        self.rows_len = len(self.rows)

        for i, row in enumerate(self.rows):
            try:
                self._do_one(i, row)
            except Exception:
                raise Exception(json.dumps(row, indent=4, ensure_ascii=False))

        print()
        for ident, ident_rows_count in self.idents.items():
            if ident_rows_count < 2:
                continue
            logger.warning(f'{ident}: {ident_rows_count}')

        # exit()

    def _do_one(self, i: int, row: Dict) -> cv_models.CV:
        ident = self._get_row_ident(row)
        if ident not in self.idents:
            self.idents[ident] = 0
        self.idents[ident] += 1

        cv = cv_models.CV.objects.filter(attributes__contains={'fw_json_import_ident': ident}).first()
        cv_created = False
        if not cv:
            cv_created = True
            cv = cv_models.CV(attributes={'fw_json_import_ident': ident})

        log_msg = f'{i + 1}/{self.rows_len}\t{"+" if cv_created else ""}\t{ident}'

        if not cv_created and self.skip_exists:
            logger.info(log_msg + '\tSKIP')
            return cv

        cv.last_name = row['lastName'] or None
        cv.first_name = row['firstName'] or None
        cv.middle_name = row['middleName'] or None
        cv.attributes['fw_json'] = row

        if row['birthDate']:
            cv.birth_date = date_parse(row['birthDate'])

        country_name = self._str_prepare(row['location']['countryName'])
        country = None
        if country_name:
            country = self.countries.get(country_name)
            if not country:
                country = dictionary_models.Country.objects.get_or_create(name=country_name)[0]
                self.countries[country_name] = country
            cv.country = country

        city_name = self._str_prepare(row['location']['name'])
        if city_name:
            city = self.cities.get(city_name)
            if not city:
                city = dictionary_models.City.objects.get_or_create(
                    name=city_name,
                    country_id=country.id if country else 1  # Россия
                )[0]
                self.cities[city_name] = city
            cv.city = city

        cv.save()

        if not cv_created:
            cv_models.CvContact.objects.filter(cv=cv).delete()
            cv_models.CvPosition.objects.filter(cv=cv).delete()
            cv_models.CvCareer.objects.filter(cv=cv).delete()
            cv_models.CvEducation.objects.filter(cv=cv).delete()
            cv_models.CvCertificate.objects.filter(cv=cv).delete()

        contacts_for_create = []
        for contact_type_name, contact_value in [
            ['email', self._get_row_contact_by_type(row, 'email')],
            ['Телефон', self._get_row_contact_by_type(row, 'mobile')],
            *[
                [_['type_field'], _['value']] for _ in row['links']
            ]
        ]:
            if not contact_value:
                continue
            contact_type_name = self._str_prepare(contact_type_name)
            contact_type = self.contact_types.get(contact_type_name)
            if not contact_type:
                contact_type = dictionary_models.ContactType.objects.get_or_create(name=contact_type_name)[0]
                self.contact_types[contact_type_name] = contact_type
            contacts_for_create.append(
                cv_models.CvContact(cv=cv, value=contact_value, contact_type=contact_type)
            )
        if contacts_for_create:
            cv_models.CvContact.objects.bulk_create(contacts_for_create)

        position_name = self._str_prepare(row['position'])
        position_year_started = None
        cv_position = None
        if not position_name:
            if row['experience']:
                position_name = self._str_prepare(row['experience'][0]['position'])
                position_year_started = row['experience'][0]['fromYear']
                for _ in row['experience']:
                    if position_name == self._str_prepare(_['position']):
                        position_year_started = min(position_year_started, _['fromYear'])
        if position_name:
            cv_position = cv_models.CvPosition.objects.create(
                cv=cv, title=position_name, year_started=position_year_started)
        if cv_position and not self.without_skills:
            skills = set(list(map(lambda x: x[:499], map(self._str_prepare, row['skills']))))
            if skills:
                for skill in skills - (set(self.competencies.keys()) & skills):
                    competence = dictionary_models.Competence.objects.filter(name=skill).first()
                    if not competence:
                        competence = dictionary_models.Competence.objects.create(name=skill)
                    self.competencies[skill] = competence
                competencies_for_create = [
                    cv_models.CvPositionCompetence(
                        cv_position=cv_position,
                        competence=self.competencies[skill]
                    )
                    for skill in skills
                ]
                if competencies_for_create:
                    cv_models.CvPositionCompetence.objects.bulk_create(competencies_for_create)

        career_for_create = []
        for experience in row['experience']:
            organization_name = (self._str_prepare(experience['company']) or 'ИП Тайна П.М.')[:499]
            organization = self.organizations.get(organization_name)
            if not organization:
                organization = main_models.Organization.objects.get_or_create(
                    name=organization_name)[0]
                self.organizations[organization_name] = organization
            career_for_create.append(
                cv_models.CvCareer(
                    cv=cv,
                    organization=organization,
                    title=experience['position'],
                    description=experience['description'],
                    date_from=(
                        datetime.date(year=experience['fromYear'], month=max(experience['fromMonth'] or -1, 1), day=1)
                        if experience['fromYear'] and experience['fromYear'] > 0
                        else None
                    ),
                    date_to=(
                        datetime.date(year=experience['toYear'], month=max(experience['toMonth'] or -1, 1), day=1)
                        if experience['toYear'] and experience['toYear'] > 0
                        else None
                    ),
                )
            )
        if career_for_create:
            cv_models.CvCareer.objects.bulk_create(career_for_create)

        education_for_create = []
        for education in row['education']:
            education_place_name = self._str_prepare(education['university'])
            education_place = None
            if education_place_name:
                education_place = self.education_places.get(education_place_name)
                if not education_place:
                    education_place = dictionary_models.EducationPlace.objects.get_or_create(
                        name=education_place_name)[0]
                    self.education_places[education_place] = education_place
            education_speciality_name = self._str_prepare(education['faculty'])
            education_speciality = None
            if education_speciality_name:
                education_speciality = self.education_specialities.get(education_speciality_name)
                if not education_speciality:
                    education_speciality = dictionary_models.EducationSpecialty.objects.get_or_create(
                        name=education_speciality_name)[0]
                    self.education_specialities[education_speciality_name] = education_speciality
            education_for_create.append(
                cv_models.CvEducation(
                    cv=cv,
                    education_place=education_place,
                    education_speciality=education_speciality,
                    date_to=(
                        datetime.date(year=education['graduateYear'], month=6, day=15)
                        if education['graduateYear'] and education['graduateYear'] > 0 else None
                    )
                )
            )
        if education_for_create:
            cv_models.CvEducation.objects.bulk_create(education_for_create)

        certificate_for_create = []
        for course in row['courses']:
            education_place_name = self._str_prepare(course['organization'])
            education_place = None
            if education_place_name:
                education_place = self.education_places.get(education_place_name)
                if not education_place:
                    education_place = dictionary_models.EducationPlace.objects.get_or_create(
                        name=education_place_name)[0]
                    self.education_places[education_place] = education_place
            certificate_for_create.append(
                cv_models.CvCertificate(
                    cv=cv,
                    education_place=education_place,
                    date=(
                        datetime.date(year=course['year'], month=6, day=15)
                        if course['year'] and course['year'] > -1
                        else None
                    ),
                    name=course['name'],
                )
            )
        if certificate_for_create:
            cv_models.CvCertificate.objects.bulk_create(certificate_for_create)

        logger.info(log_msg)

        return cv

    @classmethod
    def _str_prepare(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        return value.replace('\/', '/').replace('<br />', '\n').replace('<br>', '\n').strip()

    @classmethod
    def _get_row_contact_by_type(cls, row: Dict, contact_type: str) -> Optional[str]:
        for _ in row['contacts']:
            if _['type'].lower() == contact_type:
                return _['value']

    @classmethod
    def _get_row_ident(cls, row: Dict) -> str:
        return str(row['candidateId'])
        return re.sub(
            r'[^a-z0-9\.]',
            '_',
            translit(
                '.'.join([
                    _ for _ in [
                        row['lastName'],
                        row['firstName'],
                        row['middleName'],
                        cls._get_row_contact_by_type(row, 'email'),
                        cls._get_row_contact_by_type(row, 'mobile'),
                        row['location'].get('countryName'),
                        row['location'].get('name'),
                    ]
                    if _
                ]),
                language_code='ru',
                reversed=True,
            ).lower()
        )
