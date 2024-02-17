ADD_RECORD_FORMAT = ("<name> <second_name> <middle_name> <organisation> <org_phone> <personal_phone>\n"
                     "Example: Vasya Pupkin Ivanovich Gazprom 12345 89214444444")

UPDATE_RECORD_FORMAT = (
    "<id of record to update> name=<new name> second_name=<new second name> middle_name=<new middle name> organisation=<new organisation> org_phone<new org_phone> personal_phone=<new personal_phone>\n"
    "Example: 1 organisation=Gazprom personal_phone=+79214444444")

FIND_RECORD_FORMAT = (
    "id=<id> name=<name> second_name=<second_name> middle_name=<middle_name> organisation=<organisation> org_phone=<org_phone> personal_phone=<personal_phone>\n"
    "You can skip fields\n"
    "Example: name=Bob organisation=Gazprom ")

RECORDS_BY_PAGE_FORMAT = "<page number>\nExample: 1"

SHOULD_BE_INT_ERROR = "Error: id should be integer."
NO_RECORDS_FOUND = "No records found on this page."

MAIN_MENU_TEXT = (
    "1. Add record\n"
    "2. Update record\n"
    "3. Find records\n"
    "4. Get records by pages\n"
    "5. Exit")
