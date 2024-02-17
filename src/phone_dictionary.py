import asyncio

from db.core import DBManager
from db.tables import Record
import re

from src.Errors import NameValidationError, ValidationError


def _check_fields_appearance(**kwargs) -> bool:
    return all([field in kwargs for field in Record.__annotations__][1:])


class PhoneDictionary:
    PERSONAL_PHONE_REG = r'^(8|\+7)\d{10}'
    ORG_PHONE_REG = r'^\d{5}'
    NAME_REG = r'^[a-zA-Z]*|[а-яА-Я]*$'
    TEXT_FORMAT_COMMENT = "English or Russian letters"
    ORG_PHONE_ERROR_COMMENT = "5 digits. Example: 74244"
    PERSONAL_PHONE_ERROR_COMMENT = "Phone number starts with +7 or 8 with continuation of 10 digits. Example: +79101459029 or 89101459029"

    ERROR_COMMENT_MAP = {
        Record.name.key: (NAME_REG, TEXT_FORMAT_COMMENT),
        Record.middle_name.key: (NAME_REG, TEXT_FORMAT_COMMENT),
        Record.second_name.key: (NAME_REG, TEXT_FORMAT_COMMENT),
        Record.organisation.key: (NAME_REG, TEXT_FORMAT_COMMENT),
        Record.org_phone.key: (ORG_PHONE_REG, ORG_PHONE_ERROR_COMMENT),
        Record.personal_phone.key: (PERSONAL_PHONE_REG, PERSONAL_PHONE_ERROR_COMMENT)
    }

    def __init__(self) -> None:
        self.db_manager = DBManager()

    @staticmethod
    def _convert_name(name: str) -> str:
        return name.strip().capitalize()

    @staticmethod
    def _convert_personal_phone(phone: str) -> str:
        phone = phone.strip()
        if len(phone) == 11 and phone[0] == '8':
            phone = '+7' + phone[1:]
        return phone

    @staticmethod
    def _validate_field(pattern: str, field: str) -> bool:
        return re.fullmatch(pattern, field) is not None

    def _validate_record(self, **kwargs) -> None:
        for field in Record.__annotations__:
            if field in kwargs and field != 'id' and not self._validate_field(self.ERROR_COMMENT_MAP[field][0], kwargs[field]):
                raise NameValidationError(
                    ValidationError.ERROR_MESSAGE.format(field, kwargs[field], self.ERROR_COMMENT_MAP[field][1]))

    def _convert_field(self, record_key: str, field: str) -> str:
        if self.ERROR_COMMENT_MAP[record_key][0] == self.PERSONAL_PHONE_REG:
            field = self._convert_personal_phone(field)
        elif self.ERROR_COMMENT_MAP[record_key][0] == self.NAME_REG:
            field = self._convert_name(field)
        return field

    def _refactor_fields(self, **kwargs) -> dict[str, str | int]:
        for field in Record.__annotations__:
            if field in kwargs and field != 'id':
                kwargs[field] = self._convert_field(field, kwargs[field])
        return kwargs

    async def get_record_by_id(self, record_id: int) -> Record | None:
        return await self.db_manager.get_record_by_id(record_id)

    def add_record(self, **kwargs) -> None:

        if not _check_fields_appearance(**kwargs):
            raise ValidationError(f"Error: Expected fields: {Record.__annotations__}")

        self._validate_record(**kwargs)
        refactored_kwargs = self._refactor_fields(**kwargs)
        asyncio.run(self.db_manager.add_record(**refactored_kwargs))

    def get_records_from_page(self, page_num: str) -> list[Record]:
        try:
            page_num = int(page_num)
        except ValueError:
            raise ValidationError("Error: Incorrect page number format. Expected number.")
        left_b, right_b = (page_num - 1) * 10 + 1, ((page_num - 1) * 10 + 10)
        records = asyncio.run(self.db_manager.get_records_in_range(left_b, right_b))
        return records

    def update_record_data(self, **kwargs) -> None:
        self._validate_record(**kwargs)
        refactored_kwargs = self._refactor_fields(**kwargs)
        if 'id' not in kwargs:
            raise ValidationError("Error: Expected id field.")
        record = asyncio.run(self.db_manager.get_record_by_id(kwargs['id']))
        if not record:
            raise ValidationError(f"Error: Record with id {kwargs['id']} not found.")
        asyncio.run(self.db_manager.update_record_by_id(kwargs['id'], **refactored_kwargs))

    def find_records(self, **kwargs) -> list[Record]:
        refactored_kwargs = self._refactor_fields(**kwargs)
        records = asyncio.run(self.db_manager.find_records(**refactored_kwargs))
        return records
