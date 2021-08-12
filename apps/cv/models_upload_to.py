import datetime
import hashlib
import random
from pathlib import Path
from typing import TYPE_CHECKING

from django.db.models import Model

if TYPE_CHECKING:
    from main.models import CV, CvPositionFile, CvCareerFile, CvFile


def cv_upload_to_prefix(instance: 'CV') -> Path:
    return (
            Path(instance.UPLOAD_TO)
            / instance.id_verbose[:3]
            / instance.id_verbose[3:6]
            / instance.id_verbose[6:]
    )


def cv_upload_to_prefix(instance: 'CV') -> Path:
    return (
            Path(instance.UPLOAD_TO)
            / instance.id_verbose[:3]
            / instance.id_verbose[3:6]
            / instance.id_verbose[6:]
    )


def cv_photo_upload_to(instance: 'CV', filename) -> Path:
    return (
            cv_upload_to_prefix(instance)
            / 'photo'
            / (
                    hashlib.sha256((str(datetime.datetime.now()) + str(random.random())).encode()).hexdigest()
                    + Path(filename).suffix
            )
    )


def cv_linked_object_upload_to_immutable(instance: Model, filename, cv_instance: 'CV') -> Path:
    return (
            cv_upload_to_prefix(cv_instance)
            / instance.UPLOAD_TO
            / (
                    hashlib.sha256((str(datetime.datetime.now()) + str(random.random())).encode()).hexdigest()
                    + Path(filename).suffix
            )
    )


def cv_file_file_upload_to(instance: 'CvFile', filename: str) -> Path:
    return cv_linked_object_upload_to_immutable(instance, filename, instance.cv)


def cv_position_file_upload_to(instance: 'CvPositionFile', filename: str) -> Path:
    return cv_linked_object_upload_to_immutable(instance, filename, instance.cv_position.cv)


def cv_career_file_upload_to(instance: 'CvCareerFile', filename: str) -> Path:
    return cv_linked_object_upload_to_immutable(instance, filename, instance.cv_career.cv)
