from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import uuid
import re

# Автор книги
class Author:
    first_name: str
    last_name: str
    bio: str

    def __init__(
        self,
        first_name: str,
        last_name: str,
        bio: str = ""
    ) -> None:
        if not isinstance(first_name, str):
            raise TypeError("first_name должен быть строкой.")
        if not first_name.strip():
            raise ValueError("first_name не может быть пустым.")
        self.first_name = first_name.strip()

        if not isinstance(last_name, str):
            raise TypeError("last_name должен быть строкой.")
        if not last_name.strip():
            raise ValueError("last_name не может быть пустым.")
        self.last_name = last_name.strip()

        if not isinstance(bio, str):
            raise TypeError("bio должен быть строкой.")
        self.bio = bio.strip()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self):
        if not self.first_name or not self.last_name:
            raise ValueError("Имя и фамилия автора обязательны.")
        print(f"Автор '{self}' готов к использованию.")


# Место книги
class Location:
    rack: str
    shelf: str

    def __init__(self, rack: str, shelf: str) -> None:
        if not isinstance(rack, str):
            raise TypeError("rack должен быть строкой.")
        if not rack.strip():
            raise ValueError("rack не может быть пустым.")
        self.rack = rack.strip()

        if not isinstance(shelf, str):
            raise TypeError("shelf должен быть строкой.")
        if not shelf.strip():
            raise ValueError("shelf не может быть пустым.")
        self.shelf = shelf.strip()

    def __str__(self) -> str:
        return f"стеллаж {self.rack}, полка {self.shelf}"


# Книга
class Book:
    title: str
    author: Author
    isbn: str
    location: Location
    is_available: bool
    current_borrower: Optional['Reader']

    def __init__(
        self,
        title: str,
        author: Author,
        isbn: str,
        location: Location
    ) -> None:
        if not isinstance(title, str):
            raise TypeError("title должен быть строкой.")
        if not title.strip():
            raise ValueError("Название книги не может быть пустым.")
        self.title = title.strip()

        self.author = author

        if not isinstance(isbn, str):
            raise TypeError("isbn должен быть строкой.")
        if not isbn.strip():
            raise ValueError("ISBN не может быть пустым.")
        self.isbn = isbn.strip()
        self.location = location
        self.is_available = True
        self.current_borrower = None

    def __str__(self) -> str:
        if self.is_available:
            status = "доступна"
        else:
            if self.current_borrower is None:
                status = "выдана (владелец неизвестен)"
            else:
                borrower = self.current_borrower
                status = f"выдана {borrower.first_name} {borrower.last_name}"
        return f"'{self.title}' ({self.author}) — {status}"

    def save(self) -> bool:
        existing_book = Book.find_by_isbn(self.isbn)
        if existing_book:
            print(f"Книга с ISBN '{self.isbn}' уже существует. Обновляем.")
            # Обновляем поля кроме ISBN
            existing_book.title = self.title
            existing_book.author = self.author
            existing_book.location = self.location
            return True
        books.append(self)
        print(f"Книга '{self}' создана и добавлена в список.")
        return True

    @classmethod
    def find_by_isbn(cls, isbn: str) -> Optional['Book']:
        import main
        for book in main.books:
            if book.isbn == isbn:
                print(f"Найдена книга: {book}")
                return book
        print(f"Книга с ISBN '{isbn}' не найдена.")
        return None

    def update_location(self, new_location: Location) -> bool:
        self.location = new_location
        print(f"Местоположение книги '{self}' обновлено.")
        return True

    def delete(self) -> bool:
        if not self.is_available:
            print(f"Невозможно удалить книгу '{self}', так как она выдана читателю.")
            return False
        if self in books:
            books.remove(self)
            print(f"Книга '{self}' удалена из списка.")
            return True
        else:
            print(f"Книга '{self}' не найдена в списке для удаления.")
            return False


# Читательский билет
class Ticket:
    ticket_id: str
    issue_date: date
    expiry_date: date
    owner: 'Reader'

    def __init__(self, owner: 'Reader') -> None:
        self.owner = owner
        self.ticket_id = str(uuid.uuid4())[:8].upper()
        self.issue_date = datetime.now().date()
        self.expiry_date = self.issue_date + timedelta(days=14)

    def __str__(self) -> str:
        return f"билет №{self.ticket_id} (до {self.expiry_date})"


# Отзыв
class Review:
    text: str
    rating: int
    author: 'Reader'
    date: datetime

    def __init__(self, text: str, rating: int, author: 'Reader') -> None:
        if not isinstance(text, str):
            raise TypeError("text должен быть строкой.")
        if not text.strip():
            raise ValueError("Текст отзыва не может быть пустым.")
        self.text = text.strip()

        if not isinstance(rating, int):
            raise TypeError("rating должен быть целым числом.")
        if not (1 <= rating <= 5):
            raise ValueError("Рейтинг должен быть от 1 до 5.")
        self.rating = rating
        self.author = author
        self.date = datetime.now()

    def update(self, new_text: str, new_rating: int) -> None:
        if not isinstance(new_text, str) or not new_text.strip():
            raise ValueError("Новый текст отзыва не может быть пустым.")
        self.text = new_text.strip()

        if not isinstance(new_rating, int):
            raise TypeError("Новый рейтинг должен быть целым числом.")
        if not (1 <= new_rating <= 5):
            raise ValueError("Рейтинг должен быть от 1 до 5.")
        self.rating = new_rating

        self.date = datetime.now()


# Читатель
class Reader:
    first_name: str
    last_name: str
    phone: str
    email: str
    reader_type: str
    borrowed_books: List[Book]
    ticket: Ticket
    review: Optional[Review]
    in_club: bool
    education_place: str

    def __init__(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        reader_type: str
    ) -> None:
        if not isinstance(first_name, str):
            raise TypeError("first_name должен быть строкой.")
        if not first_name.strip():
            raise ValueError("first_name не может быть пустым.")
        self.first_name = first_name.strip()

        if not isinstance(last_name, str):
            raise TypeError("last_name должен быть строкой.")
        if not last_name.strip():
            raise ValueError("last_name не может быть пустым.")
        self.last_name = last_name.strip()

        if not isinstance(phone, str):
            raise TypeError("phone должен быть строкой.")
        if not re.match(r"^\+7\d{10}$", phone.strip()):
            raise ValueError("Неверный формат телефона. Пример: +70000000000")
        self.phone = phone.strip()

        if not isinstance(email, str):
            raise TypeError("email должен быть строкой.")
        if not email.strip() or "@" not in email:
            raise ValueError("Некорректный email.")
        self.email = email.strip()

        if not isinstance(reader_type, str):
            raise TypeError("reader_type должен быть строкой.")
        if reader_type not in {"school", "student", "regular"}:
            raise ValueError("reader_type должен быть 'school', 'student' или 'regular'.")
        self.reader_type = reader_type

        self.borrowed_books = []
        self.ticket = Ticket(self)
        self.review = None
        self.in_club = False
        self.education_place = ""

    def take_book(self, book: Book) -> bool:
        if book.is_available:
            book.is_available = False
            book.current_borrower = self
            self.borrowed_books.append(book)
            return True
        return False

    def return_borrowed_book(self, book: Book) -> bool:
        if book in self.borrowed_books:
            book.is_available = True
            book.current_borrower = None
            self.borrowed_books.remove(book)
            return True
        return False

    def set_review(self, text: str, rating: int) -> None:
        self.review = Review(text, rating, self)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.reader_type})"

    def save(self) -> bool:
        existing_reader = Reader.find_by_name(self.first_name, self.last_name)
        if existing_reader:
            print(f"Читатель '{self}' уже существует. Обновляем данные.")
            existing_reader.phone = self.phone
            existing_reader.email = self.email
            existing_reader.reader_type = self.reader_type
            existing_reader.education_place = self.education_place
            return True
        readers.append(self)
        print(f"Читатель '{self}' создан и добавлен в список.")
        return True

    @classmethod
    def find_by_name(cls, first_name: str, last_name: str) -> Optional['Reader']:
        for reader in readers:
            if reader.first_name == first_name and reader.last_name == last_name:
                print(f"Найден читатель: {reader}")
                return reader
        print(f"Читатель '{first_name} {last_name}' не найден.")
        return None

    def update_education_place(self, new_education_place: str) -> bool:
        self.education_place = new_education_place.strip()
        print(f"Место учёбы/работы читателя '{self}' обновлено.")
        return True

    def delete(self) -> bool:
        if len(self.borrowed_books) > 0:
            print(f"Невозможно удалить читателя '{self}', у него есть невозвращённые книги.")
            return False
        if self in readers:
            readers.remove(self)
            print(f"Читатель '{self}' удалён из списка.")
            return True
        else:
            print(f"Читатель '{self}' не найден в списке для удаления.")
            return False


# Библиотекарь
class Librarian:
    ACCESS_CODE: int = 314

    first_name: str
    last_name: str
    phone: str

    def __init__(self, last_name: str, first_name: str, phone: str) -> None:
        if not isinstance(first_name, str):
            raise TypeError("first_name должен быть строкой.")
        if not first_name.strip():
            raise ValueError("first_name не может быть пустым.")
        self.first_name = first_name.strip()

        if not isinstance(last_name, str):
            raise TypeError("last_name должен быть строкой.")
        if not last_name.strip():
            raise ValueError("last_name не может быть пустым.")
        self.last_name = last_name.strip()

        if not isinstance(phone, str):
            raise TypeError("phone должен быть строкой.")
        if not re.match(r"^\+7\d{10}$", phone.strip()):
            raise ValueError("Неверный формат телефона. Пример: +70000000000")
        self.phone = phone.strip()

    @staticmethod
    def verify_code(code: int) -> bool:
        if not isinstance(code, int):
            return False
        return code == Librarian.ACCESS_CODE

    def accept_book_return(self, book: Book, reader: Reader) -> bool:
        if not book.is_available and book.current_borrower == reader:
            reader.return_borrowed_book(book)
            return True
        return False

    def lend_book_to_reader(self, book: Book, reader: Reader) -> bool:
        return reader.take_book(book)

    def edit_reader_education(self, reader: Reader, new_place: str) -> None:
        if not isinstance(new_place, str):
            raise TypeError("new_place должен быть строкой.")
        reader.education_place = new_place.strip()

    def save(self) -> bool:
        existing_librarian = Librarian.find_by_name(self.first_name, self.last_name)
        if existing_librarian:
            print(f"Библиотекарь '{self}' уже существует. Обновляем данные.")
            existing_librarian.phone = self.phone
            return True
        librarians.append(self)
        print(f"Библиотекарь '{self}' создан и добавлен в список.")
        return True

    @classmethod
    def find_by_name(cls, first_name: str, last_name: str) -> Optional['Librarian']:
        for librarian in librarians:
            if librarian.first_name == first_name and librarian.last_name == last_name:
                print(f"Найден библиотекарь: {librarian}")
                return librarian
        print(f"Библиотекарь '{first_name} {last_name}' не найден.")
        return None

    def update_phone(self, new_phone: str) -> bool:
        if not re.match(r"^\+7\d{10}$", new_phone.strip()):
            print("Неверный формат телефона.")
            return False
        self.phone = new_phone.strip()
        print(f"Телефон библиотекаря '{self}' обновлён.")
        return True

    def delete(self) -> bool:
        if self in librarians:
            librarians.remove(self)
            print(f"Библиотекарь '{self}' удалён из списка.")
            return True
        else:
            print(f"Библиотекарь '{self}' не найден в списке для удаления.")
            return False


# Школьник
class School(Reader):
    school_name: str
    grade: str

    def __init__(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        school_name: str,
        grade: str
    ) -> None:
        if not isinstance(school_name, str):
            raise TypeError("school_name должен быть строкой.")
        if not school_name.strip():
            raise ValueError("school_name не может быть пустым.")
        self.school_name = school_name.strip()

        if not isinstance(grade, str):
            raise TypeError("grade должен быть строкой.")
        if not grade.strip():
            raise ValueError("grade не может быть пустым.")
        self.grade = grade.strip()

        super().__init__(first_name, last_name, phone, email, "school")


# Студент
class Student(Reader):
    university: str
    course: int

    def __init__(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        university: str,
        course: int
    ) -> None:
        if not isinstance(university, str):
            raise TypeError("university должен быть строкой.")
        if not university.strip():
            raise ValueError("university не может быть пустым.")
        self.university = university.strip()

        if not isinstance(course, int):
            raise TypeError("course должен быть целым числом.")
        if not (1 <= course <= 6):
            raise ValueError("course должен быть от 1 до 6.")
        self.course = course

        super().__init__(first_name, last_name, phone, email, "student")


# Читательный зал
class Room:
    name: str
    seats: Dict[int, Dict[datetime, Reader]]

    def __init__(self, name: str, total_seats: int = 20) -> None:
        if not isinstance(name, str):
            raise TypeError("name должен быть строкой.")
        if not name.strip():
            raise ValueError("name не может быть пустым.")
        self.name = name.strip()

        if not isinstance(total_seats, int):
            raise TypeError("total_seats должен быть целым числом.")
        if total_seats < 1:
            raise ValueError("total_seats должен быть >= 1.")
        self.seats = {i: {} for i in range(1, total_seats + 1)}

    def is_seat_available_at(self, seat_num: int, dt: datetime) -> bool:
        if not isinstance(seat_num, int) or seat_num not in self.seats:
            return False
        if not isinstance(dt, datetime):
            return False
        return dt not in self.seats[seat_num]

    def reserve_seat(self, seat_num: int, dt: datetime, reader: 'Reader') -> bool:
        if self.is_seat_available_at(seat_num, dt):
            self.seats[seat_num][dt] = reader
            return True
        return False

    def save(self) -> bool:
        existing_room = Room.find_by_name(self.name)
        if existing_room:
            print(f"Читательский зал '{self.name}' уже существует. Обновляем (например, количество мест).")
            existing_room.name = self.name # Обновляем имя, если оно изменилось
            return True
        rooms.append(self)
        print(f"Читательский зал '{self.name}' создан и добавлен в список.")
        return True

    @classmethod
    def find_by_name(cls, name: str) -> Optional['Room']:
        for room in rooms:
            if room.name == name:
                print(f"Найден зал: {room.name}")
                return room
        print(f"Читательский зал '{name}' не найден.")
        return None

    def update_name(self, new_name: str) -> bool:
        existing_room = Room.find_by_name(new_name)
        if existing_room and existing_room != self:
             print(f"Читательский зал с названием '{new_name}' уже существует.")
             return False
        self.name = new_name.strip()
        print(f"Название зала '{self.name}' изменено на '{new_name}'.")
        return True

    def delete(self) -> bool:
        now = datetime.now()
        has_future_booking = any(
            dt >= now for times in self.seats.values() for dt in times.keys()
        )
        if has_future_booking:
            print(f"Невозможно удалить зал '{self.name}', так как в нём есть бронирования на будущее.")
            return False
        if self in rooms:
            rooms.remove(self)
            print(f"Читательский зал '{self.name}' удалён из списка.")
            return True
        else:
            print(f"Читательский зал '{self.name}' не найден в списке для удаления.")
            return False


# Читательский клуб
class Club:
    members: List[Reader]
    meetings: List[datetime]
    current_book: Optional[Book]

    def __init__(self) -> None:
        self.members = []
        self.meetings = []
        self.current_book = None

    def join(self, reader: Reader) -> None:
        if reader not in self.members:
            self.members.append(reader)
            reader.in_club = True

    def leave(self, reader: Reader) -> None:
        if reader in self.members:
            self.members.remove(reader)
            reader.in_club = False

    def add_meeting(self, dt: datetime) -> None:
        self.meetings.append(dt)

    def set_current_book(self, book: Book) -> None:
        self.current_book = book

    def save(self) -> bool:
        if self not in clubs:
            clubs.append(self)
            print(f"Читательский клуб '{id(self)}' создан и добавлен в список.")
            return True
        else:
            print(f"Читательский клуб '{id(self)}' уже существует в списке.")
            return True

    def find_by_index(cls, index: int) -> Optional['Club']:
        if 0 <= index < len(clubs):
            club = clubs[index]
            print(f"Найден клуб: {id(club)}")
            return club
        print(f"Читательский клуб с индексом {index} не найден.")
        return None

    def set_current_book_crud(self, new_book: Book) -> bool:
        self.set_current_book(new_book)
        print(f"Текущая книга клуба '{id(self)}' обновлена на '{new_book}'.")
        return True

    def delete(self) -> bool:
        if len(self.members) > 0:
            print(f"Невозможно удалить клуб '{id(self)}', так как в нём есть члены.")
            return False
        if self in clubs:
            clubs.remove(self)
            print(f"Читательский клуб '{id(self)}' удалён из списка.")
            return True
        else:
            print(f"Читательский клуб '{id(self)}' не найден в списке для удаления.")
            return False

from main import books, readers, librarians, rooms, clubs # Импортглобальных списков из main для хранения данных
