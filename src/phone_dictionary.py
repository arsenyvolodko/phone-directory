import asyncio
import re

from db.core import DBManager
from db.tables import Record

from src.Errors import NameValidationError, ValidationError


def _check_fields_appearance(**kwargs) -> bool:
    """
    Checks if the essential fields are present in the provided arguments.

    :param kwargs: Keyword arguments representing the fields to check.
    :return: True if all required fields are present, False otherwise.
    """
    return all([field in kwargs for field in Record.__annotations__][1:])


class PhoneDictionary:
    """
    A class representing a phone directory that allows for storing,
    retrieving, and updating records with validation.
    """
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
        """
        Initializes the PhoneDictionary with a DBManager instance.
        """
        self.db_manager = DBManager()

    @staticmethod
    def _convert_name(name: str) -> str:
        """
        Converts a name to a standardized format (stripped and capitalized).

        :param name: The name to convert.
        :return: The converted name.
        """
        return name.strip().capitalize()

    @staticmethod
    def _convert_personal_phone(phone: str) -> str:
        """
        Converts a personal phone number to a standard format, ensuring it starts with +7.

        :param phone: The phone number to convert.
        :return: The converted phone number.
        """
        phone = phone.strip()
        if len(phone) == 11 and phone[0] == '8':
            phone = '+7' + phone[1:]
        return phone

    @staticmethod
    def _validate_field(pattern: str, field: str) -> bool:
        """
        Validates a field against a given pattern.

        :param pattern: The regex pattern to validate against.
        :param field: The field value to validate.
        :return: True if the field matches the pattern, False otherwise.
        """
        return re.fullmatch(pattern, field) is not None

    def _validate_record(self, **kwargs) -> None:
        """
        Validates the fields of a record against predefined patterns.

        :param kwargs: Keyword arguments representing the fields to validate.
        :raises NameValidationError: If a field does not conform to its validation pattern.
        """
        for field in Record.__annotations__:
            if field in kwargs and field != 'id' and not self._validate_field(self.ERROR_COMMENT_MAP[field][0],
                                                                              kwargs[field]):
                raise NameValidationError(
                    ValidationError.ERROR_MESSAGE.format(field, kwargs[field], self.ERROR_COMMENT_MAP[field][1]))

    def _convert_field(self, record_key: str, field: str) -> str:
        """
        Converts a field based on its key to a standardized format.

        :param record_key: The key of the record field.
        :param field: The value of the field to convert.
        :return: The converted field value.
        """
        if self.ERROR_COMMENT_MAP[record_key][0] == self.PERSONAL_PHONE_REG:
            field = self._convert_personal_phone(field)
        elif self.ERROR_COMMENT_MAP[record_key][0] == self.NAME_REG:
            field = self._convert_name(field)
        return field

    def _refactor_fields(self, **kwargs) -> dict[str, str | int]:
        """
        Refactors the fields of a record for standardization and validation.

        :param kwargs: Keyword arguments representing the record fields.
        :return: A dictionary of the refactored fields.
        """
        for field in Record.__annotations__:
            if field in kwargs and field != 'id':
                kwargs[field] = self._convert_field(field, kwargs[field])
        return kwargs

    async def get_record_by_id(self, record_id: int) -> Record | None:
        """
        Retrieves a record by its ID.

        :param record_id: The ID of the record to retrieve.
        :return: The Record object if found, None otherwise.
        """
        return await self.db_manager.get_record_by_id(record_id)

    def add_record(self, **kwargs) -> None:
        """
        Adds a new record to the phone directory after validation and conversion.

        :param kwargs: Keyword arguments representing the record fields.
        :raises ValidationError: If expected fields are missing or validation fails.
        """
        if not _check_fields_appearance(**kwargs):
            raise ValidationError(f"Error: Expected fields: {list(Record.__annotations__.keys())[1:]}")

        self._validate_record(**kwargs)
        refactored_kwargs = self._refactor_fields(**kwargs)
        asyncio.run(self.db_manager.add_record(**refactored_kwargs))

    def get_records_from_page(self, page_num: str) -> list[Record]:
        """
        Retrieves records for a specific page number, assuming a fixed number of records per page.

        :param page_num: The page number to retrieve records for.
        :return: A list of Record objects for the specified page.
        :raises ValidationError: If the page number is not a valid integer.
        """
        try:
            page_num = int(page_num)
        except ValueError:
            raise ValidationError("Error: Incorrect page number format. Expected number.")
        left_b, right_b = (page_num - 1) * 10 + 1, ((page_num - 1) * 10 + 10)
        records = asyncio.run(self.db_manager.get_records_in_range(left_b, right_b))
        return records

    def update_record_data(self, **kwargs) -> None:
        """
        Updates the data of an existing record in the directory.

        :param kwargs: Keyword arguments representing the fields to update, including the record ID.
        :raises ValidationError: If the ID field is missing or the record does not exist.
        """
        self._validate_record(**kwargs)
        refactored_kwargs = self._refactor_fields(**kwargs)
        if 'id' not in kwargs:
            raise ValidationError("Error: Expected id field.")
        record = asyncio.run(self.db_manager.get_record_by_id(kwargs['id']))
        if not record:
            raise ValidationError(f"Error: Record with id {kwargs['id']} not found.")
        asyncio.run(self.db_manager.update_record_by_id(kwargs['id'], **refactored_kwargs))

    def find_records(self, **kwargs) -> list[Record]:
        """
        Finds records matching the specified fields.

        :param kwargs: Keyword arguments representing the fields to match.
        :return: A list of Record objects matching the specified fields.
        """
        refactored_kwargs = self._refactor_fields(**kwargs)
        records = asyncio.run(self.db_manager.find_records(**refactored_kwargs))
        return records
