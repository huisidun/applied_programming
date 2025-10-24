from datetime import datetime
from classes import Reader, Review, Book, Author, Location

def test_exceptions():
    print("тест создания объектов с невалидными данными\n")

    # Невалидный email
    print("1. Попытка создать читателя с невалидным email:")
    try:
        reader = Reader("Василиса", "Петрова", "+79090909090", "это не email", "student")
        print("Читатель создан (ошибка!)")
    except ValueError as e:
        print(f"Ошибка: {e}")
    print("-" * 60)

    # Невалидный рейтинг
    print("Попытка создать отзыв с рейтингом 7:")
    try:
        reader = Reader("Иван", "Иванов", "+71234567890", "ivan@test.com", "regular")
        review = Review("Отлично!", 7, reader)
        print("Отзыв создан (ошибка!)")
    except ValueError as e:
        print(f"Ошибка: {e}")
    print("=" * 60)
    print("Тестирование завершено.")

if __name__ == "__main__":
    test_exceptions()