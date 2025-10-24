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