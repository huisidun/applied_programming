# test_crud_classes.py

# Импортируем классы из нового файла
from classes import Author, Location, Book, Reader, Librarian, Student, Room, Club # Используем файл с CRUD методами

# Импортируем main ПОСЛЕ определения классов, чтобы убедиться, что он полностью загружен
# Это позволяет получить доступ к глобальным спискам.
import main

def test_crud():
    print("--- Тестирование CRUD методов в классах ---")

    # --- Подготовка ---
    print("\n--- Подготовка: очистка списков для теста ---")
    # Сохраним длины списков до очистки
    initial_lengths = {
        'books': len(main.books),
        'readers': len(main.readers),
        'librarians': len(main.librarians),
        'rooms': len(main.rooms),
        'clubs': len(main.clubs)
    }
    print(f"Длины списков до очистки: {initial_lengths}")

    # Очищаем списки (для изолированного теста)
    main.books.clear()
    main.readers.clear()
    main.librarians.clear()
    main.rooms.clear()
    main.clubs.clear()

    print(f"Длины списков после очистки: {{'books': {len(main.books)}, 'readers': {len(main.readers)}, 'librarians': {len(main.librarians)}, 'rooms': {len(main.rooms)}, 'clubs': {len(main.clubs)}}}")


    # --- Тест Create (Save) ---
    print("\n--- Тест Create (Save) ---")
    author1 = Author("Тест", "Автор", "Био автора")
    author1.save() # Вызов метода save у объекта

    location1 = Location("R", "101")
    book1 = Book("Тестовая Книга 1", author1, "TEST-001", location1)
    book1.save() # Вызов метода save у объекта

    reader1 = Student("Тест", "Студент", "+79999999999", "test_stud@inbox.ru", "ТестУнивер", 3)
    reader1.save() # Вызов метода save у объекта

    # Создание библиотекаря: Librarian(last_name, first_name, phone)
    librarian1 = Librarian("Биб", "Тест", "+78888888888") # Исправлен порядок: фамилия, имя
    librarian1.save() # Вызов метода save у объекта

    room1 = Room("Тестовый Зал")
    room1.save() # Вызов метода save у объекта

    club1 = Club()
    club1.save() # Вызов метода save у объекта

    print(f"После создания: {{'books': {len(main.books)}, 'readers': {len(main.readers)}, 'librarians': {len(main.librarians)}, 'rooms': {len(main.rooms)}, 'clubs': {len(main.clubs)}}}")


    # --- Тест Read (Find) ---
    print("\n--- Тест Read (Find) ---")
    found_book = Book.find_by_isbn("TEST-001") # Вызов метода класса
    if found_book:
        print(f"Найдена книга: {found_book}")
    else:
        print("Книга не найдена!")

    found_reader = Reader.find_by_name("Тест", "Студент") # Вызов метода класса
    if found_reader:
        print(f"Найден читатель: {found_reader}")
    else:
        print("Читатель не найден!")

    # Поиск библиотекаря: Librarian.find_by_name(first_name, last_name)
    # Параметры в find_by_name(first_name, last_name), а создавали Librarian("Биб", "Тест")
    # Поэтому ищем как ("Тест", "Биб") - first_name="Тест", last_name="Биб"
    found_librarian = Librarian.find_by_name("Тест", "Биб") # Исправлен вызов: имя, фамилия
    if found_librarian:
        print(f"Найден библиотекарь: {found_librarian}")
    else:
        print("Библиотекарь не найден!")

    found_room = Room.find_by_name("Тестовый Зал") # Вызов метода класса
    if found_room:
        print(f"Найден зал: {found_room.name}")
    else:
        print("Зал не найден!")


    # --- Тест Update ---
    print("\n--- Тест Update ---")
    if found_book:
        new_location = Location("R", "202")
        found_book.update_location(new_location) # Вызов метода экземпляра
        print(f"Местоположение книги обновлено: {found_book.location}")

    if found_reader:
        found_reader.update_education_place("Новое Учебное Заведение") # Вызов метода экземпляра
        print(f"Место учёбы читателя обновлено: {found_reader.education_place}")

    if found_librarian:
        success = found_librarian.update_phone("+77777777777") # Вызов метода экземпляра
        if success:
            print(f"Телефон библиотекаря обновлён: {found_librarian.phone}")


    # --- Тест Delete ---
    print("\n--- Тест Delete ---")
    if found_book:
        print(f"Удаляем книгу: {found_book}")
        success = found_book.delete() # Вызов метода экземпляра
        print(f"Удаление прошло успешно: {success}")
        print(f"Количество книг после удаления: {len(main.books)}")

    if found_reader:
        print(f"Удаляем читателя: {found_reader}")
        success = found_reader.delete() # Вызов метода экземпляра
        print(f"Удаление прошло успешно: {success}")
        print(f"Количество читателей после удаления: {len(main.readers)}")

    if found_librarian:
        print(f"Удаляем библиотекаря: {found_librarian}")
        success = found_librarian.delete() # Вызов метода экземпляра
        print(f"Удаление прошло успешно: {success}")
        print(f"Количество библиотекарей после удаления: {len(main.librarians)}")


    # --- Проверка финального состояния списков ---
    print("\n--- Финальное состояние списков ---")
    print(f"Книг: {len(main.books)}")
    print(f"Читателей: {len(main.readers)}")
    print(f"Библиотекарей: {len(main.librarians)}")
    print(f"Залов: {len(main.rooms)}")
    print(f"Клубов: {len(main.clubs)}")

    # --- Восстановление ---
    print("\n--- Восстановление: очистка списков после теста ---")
    main.books.clear()
    main.readers.clear()
    main.librarians.clear()
    main.rooms.clear()
    main.clubs.clear()
    print(f"Списки снова пусты: {{'books': {len(main.books)}, 'readers': {len(main.readers)}, 'librarians': {len(main.librarians)}, 'rooms': {len(main.rooms)}, 'clubs': {len(main.clubs)}}}")


if __name__ == "__main__":
    test_crud()
