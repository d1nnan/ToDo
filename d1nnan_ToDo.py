import sqlite3
import json


class MyEncoder(json.JSONEncoder):
    """Класс кодировщика.."""

    def default(self, tasks):
        if isinstance(tasks, ToDo):
            return tasks.__dict__


class NameExc(Exception):
    """Класс исключение, вызывется когда ввод названия задания невалиден."""

    def __init__(self, head="ToDoTaskNameError", message="Bad name!"):
        super().__init__(message)
        self.head = head
        self.message = message


class PriorityExc(Exception):
    """Класс исключение, вызывается когда ввод приоритета невалиден."""

    def __init__(self, head="ToDoPriorityError", message="Bad priority!"):
        super().__init__(message)
        self.head = head
        self.message = message


class IdExc(Exception):
    """Класс исключение, вызывается когда id невалиден."""

    def __init__(self, head="ToDoIDError", message="Bad ID!"):
        super().__init__(message)
        self.head = head
        self.message = message


class ToDo:
    def __init__(self):
        self.conn = sqlite3.connect("todo3.db")
        self.cursor = self.conn.cursor()
        self.create_tasks_table()

    def create_tasks_table(self):
        """Создание таблицы с заданиями."""

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL, 
        priority INTEGER NOT NULL
        );"""
        )

    def add_task(self):
        """Функция, добавляющая дело."""

        self.task_name = input("Введите имя задания: ")
        if len(self.task_name) == 0 or self.task_name.isspace():
            raise NameExc

        search_same_name = self.find_task(self.task_name)
        if search_same_name is not None:
            raise NameExc(message="Имя уже занято!")

        self.task_priority = int(input("Введите приоритет:"))
        if self.task_priority < 1:
            raise PriorityExc

        self.cursor.execute(
            "INSERT INTO tasks (name, priority) VALUES (?, ?)",
            (self.task_name, self.task_priority),
        )
        self.conn.commit()

    def find_task(self, task_name):
        """Поиск на сущестование имени задания."""

        self.task_name = task_name

        self.rows = self.cursor.execute("""SELECT id, name, priority FROM tasks;""")

        for row in self.rows:
            if row[1] == self.task_name:
                return row

    def show_tasks(self):
        """Отображает список заданий."""

        print("Таблица содержит следующие задания:")
        print("ID    |  Task name   |  Priority ")
        for row in self.cursor.execute("""SELECT * FROM tasks;"""):
            print(row)

    def update_priority(self):
        """Позволяет редактировать приоритет существующего задания."""

        self.task_id = int(input("Введите id задания: "))
        if self.task_id < 1:
            raise IdExc

        self.task_priority = int(input("Введите новый приоритет: "))
        if self.task_priority < 1:
            raise PriorityExc

        self.cursor.execute(
            "UPDATE tasks SET priority = ? WHERE id = ?;",
            (self.task_priority, self.task_id),
        )
        self.conn.commit()

    def update_name(self):
        """Позволяет редактировать имя существующего задания."""

        self.task_id = int(input("Введите id задания: "))
        if self.task_id < 1:
            raise IdExc

        self.task_name = input("Введите новое имя: ")
        if self.task_name == 0 or self.task_name.isspace():
            raise NameExc

        self.cursor.execute(
            "UPDATE tasks SET name = ? WHERE id = ?;", (self.task_name, self.task_id)
        )
        self.conn.commit()

    def delete_task(self):
        """Позволяет удалить существующее задание."""

        self.task_id = int(input("Введите id задания: "))
        if self.task_id < 1:
            raise IdExc

        self.cursor.execute("""DELETE FROM tasks WHERE id = ?;""", (self.task_id,))
        self.conn.commit()

    def close_connection(self):
        """Закрывает поток в БД."""

        print("Пока!!")
        self.conn.close()

    def record_json(self):
        """Перезаписывает таблицу БД в список словарей,
        а затем затем кодирует словарь и записывает его в json-файл."""

        self.cursor.execute("SELECT * FROM tasks")
        table = []
        attributes = ["id", "name", "priority"]
        for row in self.cursor.fetchall():
            task = dict(zip(attributes, row))
            table.append(task)
        with open("result.json", "wt") as outfile:
            json.dump(json.dumps(table, cls=MyEncoder), outfile)


def menu_controller(app: ToDo, user_input):
    """Ответ на пользовательский ввод."""

    if user_input == 1:
        app.add_task()
    elif user_input == 2:
        task_to_find = input("Введите название задания, которое надо найти: ")
        if app.find_task(task_to_find):
            print("Найдено!", app.find_task(task_to_find))
        else:
            print(f"{task_to_find} не найдено")
    elif user_input == 3:
        print("Ниже приведен список заданий")
        app.show_tasks()
    elif user_input == 4:
        app.update_priority()
        print("Приоритет успешно изменен!")
    elif user_input == 5:
        app.update_name()
        print("Имя успешно изменено")
    elif user_input == 6:
        app.delete_task()
        print("Задание успешно удалено")
    elif user_input == 7:
        app.record_json()
        print("Успех")
    else:
        print("неправильный ввод")


def main():
    appy = ToDo()
    print(
        "Список доступных действий:\n1. Добавить задание\n\
2. Найти задание\n3. Отобразить список заданий\n\
4. Изменить приоритет задания\n\
5. Изменить название задания\n6. Удалить задание\n7. Вывести список дел в json-файл\n\
8. Завершить работу"
    )
    user_input = int(input("Ваш выбор: "))
    while user_input != 8:
        menu_controller(appy, user_input)
        print()
        user_input = int(input("Повторите выбор или нажмите 8: "))

    appy.close_connection()


if __name__ == "__main__":
    print("main запущен сам по себе")
    main()
else:
    print("main запущен как встраиваемый модуль")
