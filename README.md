## SIMPLE PHONE DIRECTORY

### Description
Асинхронная утилита для работы с телефонным справочником из командной строки. Позволяет добавлять, редактировать и просматривать записи в базе данных с использованием фильтров.

### Installation
```bash
poetry shell
poetry install --no-root
python3 main.py
```

### Usage
После запуска программы вам будет предложено ввести команду, после чего - ввести необходимые для запроса данные. Доступные команды:
* 1 - Добавить запись. 
Формат ввода: `<name> <second_name> <middle_name> <organisation> <org_phone> <personal_phone>`.\
Например: `Иван Иванов Иванович Газпром 56733 +79101459029`.
Это позволит добавить в телефонный справочник новую запись.
* 2 - Редактировать запись.
Формат ввода: `<id> name=<name> second_name=<second_name> middle_name=<middle_name> organisation=<organisation> org_phone=<org_phone> personal_phone=<personal_phone>`.
Например: `20 org_phone=56733 personal_phone=+79101459029`.
Это поменяет номер организации и личный номер телефона у записи с id=20.
* 3 - Просмотреть записи по фильтрам.
Формат ввода: `id=<id> name=<name> second_name=<second_name> middle_name=<middle_name> organisation=<organisation> org_phone=<org_phone> personal_phone=<personal_phone>`.
Например: `name=Bob organisation=Gazprom`.
Это покажет все записи, у которых поле имя - Bob и организация - Gazprom. Если не указать ни одного фильтра, будут показаны все записи.
* 4 - Вывести все записи на определенной странице.
Формат ввода: `<page_number>`.
Например: `2`.
Это покажет все записи на второй странице. На каждой странице ровно 10 записей.
* 5 - Завершить работу программы.

