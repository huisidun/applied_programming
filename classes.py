from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import uuid

# Автор 
class Author:
    first_name: str
    last_name: str
    bio: str

    def __init__(self, first_name: str, last_name: str, bio: str = "") -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


# Место книги (Location)
class Location:
    rack: str
    shelf: str

    def __init__(self, rack: str, shelf: str) -> None:
        self.rack = rack
        self.shelf = shelf

    def __str__(self) -> str:
        return f"стеллаж {self.rack}, полка {self.shelf}"


#книга (Book)
class Book:
    title: str
    author: Author
    isbn: str
    location: Location
    is_available: bool
    current_borrower: Optional['Reader']

    def __init__(self, title: str, author: Author, isbn: str, location: Location) -> None:
        self.title = title
        self.author = author
        self.isbn = isbn
        self.location = location
        self.is_available = True
        self.current_borrower = None

    def __str__(self) -> str:
        if self.is_available:
            status = "доступна"
        else:
            borrower = self.current_borrower
            status = f"выдана {borrower.first_name} {borrower.last_name}"
        return f"'{self.title}' ({self.author}) — {status}"


#читательский билет (Ticket)
class Ticket:
    ticket_id: str
    issue_date: date
    expiry_date: date
    owner: 'Reader'

    def __init__(self, owner: 'Reader') -> None:
        self.ticket_id = str(uuid.uuid4())[:8].upper()
        self.issue_date = datetime.now().date()
        self.expiry_date = self.issue_date + timedelta(days=14)
        self.owner = owner

    def __str__(self) -> str:
        return f"билет №{self.ticket_id} (до {self.expiry_date})"


#отзыв (Review) 
class Review:
    text: str
    rating: int
    author: 'Reader'
    date: datetime

    def __init__(self, text: str, rating: int, author: 'Reader') -> None:
        if not (1 <= rating <= 5):
            raise ValueError("рейтинг от 1 до 5")
        self.text = text
        self.rating = rating
        self.author = author
        self.date = datetime.now()

    def update(self, new_text: str, new_rating: int) -> None:
        if not (1 <= new_rating <= 5):
            raise ValueError("рейтинг от 1 до 5")
        self.text = new_text
        self.rating = new_rating
        self.date = datetime.now()


#читатель (Reader)
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

    def __init__(self, first_name: str, last_name: str, phone: str, email: str, reader_type: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.reader_type = reader_type  # "school", "student", "regular"
        self.borrowed_books = []
        self.ticket = Ticket(self)
        self.review = None
        self.in_club = False
        self.education_place = ""  #редактирует только библиотекарь

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
        if self.review is None:
            self.review = Review(text, rating, self)
        else:
            self.review.update(text, rating)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.reader_type})"


#библиотекарь (Librarian)
class Librarian:
    ACCESS_CODE: int = 314  #код входа в систему

    first_name: str
    last_name: str
    phone: str

    def __init__(self, last_name: str, first_name: str, phone: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
    
    def verify_code(code: int) -> bool:
        return code == Librarian.ACCESS_CODE

    def accept_book_return(self, book: Book, reader: Reader) -> bool:
        if not book.is_available and book.current_borrower == reader:
            reader.return_borrowed_book(book)
            return True
        return False

    def lend_book_to_reader(self, book: Book, reader: Reader) -> bool:
        return reader.take_book(book)

    def edit_reader_education(self, reader: Reader, new_place: str) -> None:
        reader.education_place = new_place


#школьник (School)
class School(Reader):
    school_name: str
    grade: str

    def __init__(self, first_name: str, last_name: str, phone: str, email: str, school_name: str, grade: str) -> None:
        super().__init__(first_name, last_name, phone, email, "school")
        self.school_name = school_name
        self.grade = grade


#студент (Student)
class Student(Reader):
    university: str
    course: int

    def __init__(self, first_name: str, last_name: str, phone: str, email: str, university: str, course: int) -> None:
        super().__init__(first_name, last_name, phone, email, "student")
        self.university = university
        self.course = course


#читательный зал (Room)
class Room:
    name: str
    seats: Dict[int, Dict[datetime, Reader]]

    def __init__(self, name: str, total_seats: int = 20) -> None:
        self.name = name
        self.seats = {
            i: {} for i in range(1, total_seats + 1)
        }

    def is_seat_available_at(self, seat_num: int, dt: datetime) -> bool:
        if seat_num not in self.seats:
            return False
        return dt not in self.seats[seat_num]

    def reserve_seat(self, seat_num: int, dt: datetime, reader: 'Reader') -> bool:
        if self.is_seat_available_at(seat_num, dt):
            self.seats[seat_num][dt] = reader
            return True
        return False


#читательский клуб (Club)
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
