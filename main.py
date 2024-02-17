from src.phone_dictionary import PhoneDictionary, ValidationError
from db.tables import Record
from consts import *


class STATE:
    MAIN = 0
    ADD_RECORD = 1
    UPDATE_RECORD = 2
    FIND_RECORD = 3
    GET_RECORDS_BY_PAGES = 4


def convert_input_to_dict(input_str: str, to_update: bool) -> dict[str, str | int]:
    input_list = input_str.split()
    res = {}
    if to_update:
        res['id'] = int(input_list[0])
        input_list = input_list[1:]
    for i in input_list:
        key, value = i.split('=')
        if key not in Record.__annotations__:
            raise ValidationError(f"Error: Unknown field {key}.")
        res[key] = value
    return res


def get_info_print_message(expected_format: str):
    return f"Enter record data in format:\n{expected_format}"


def handle_main_action(action):
    global cur_state
    if cur_state == STATE.MAIN:
        match action:
            case "1":
                print(get_info_print_message(ADD_RECORD_FORMAT))
                cur_state = STATE.ADD_RECORD
            case "2":
                print(get_info_print_message(UPDATE_RECORD_FORMAT))
                cur_state = STATE.UPDATE_RECORD
            case "3":
                print(get_info_print_message(FIND_RECORD_FORMAT))
                cur_state = STATE.FIND_RECORD
            case "4":
                print(get_info_print_message(RECORDS_BY_PAGE_FORMAT))
                cur_state = STATE.GET_RECORDS_BY_PAGES
            case "5":
                exit(0)
            case _:
                print("Unknown action")
    return


def handle_action(action):
    global cur_state
    if cur_state == STATE.ADD_RECORD:
        cur_state = STATE.MAIN
        action_list = action.split()
        if len(action_list) != 6:
            print("Incorrect number of fields. Expected 6.")
            return
        new_record = {'name': action_list[0], 'second_name': action_list[1], 'middle_name': action_list[2],
                      'organisation': action_list[3], 'org_phone': action_list[4], 'personal_phone': action_list[5]}
        try:
            pd.add_record(**new_record)
        except ValidationError as e:
            print(e)
            return
        print("Record added.")

    elif cur_state == STATE.UPDATE_RECORD:
        cur_state = STATE.MAIN
        try:
            record_to_update = convert_input_to_dict(action, True)
            pd.update_record_data(**record_to_update)
        except ValidationError as e:
            print(e)
            return
        except ValueError:
            print("Error: id should be integer.")
            return
        print("Record updated.")

    elif cur_state == STATE.FIND_RECORD:
        cur_state = STATE.MAIN
        try:
            record_to_find = convert_input_to_dict(action, False)
            records = pd.find_records(**record_to_find)
        except ValidationError as e:
            print(e)
            return
        except ValueError:
            print(SHOULD_BE_INT_ERROR)
            return
        print(f"Found {len(records)} records:")
        for i in records:
            print(i)

    elif cur_state == STATE.GET_RECORDS_BY_PAGES:
        cur_state = STATE.MAIN
        try:
            records = pd.get_records_from_page(action)
        except ValidationError as e:
            print(e)
            return
        print(f"Page {action}:")
        if not records:
            print(NO_RECORDS_FOUND)
            return
        for i in records:
            print(i)


def main():
    while True:
        if cur_state == STATE.MAIN:
            print(MAIN_MENU_TEXT)
            action = input()
            handle_main_action(action)
        else:
            action = input()
            handle_action(action)


if __name__ == '__main__':
    pd = PhoneDictionary()
    cur_state = STATE.MAIN
    main()
