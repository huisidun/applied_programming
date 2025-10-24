from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import uuid

# Автор 
class Author:
    def __init__(self, first_name: str, last_name: str, bio: str = ""):
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.bio: str = bio

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


# Место книги (Location)
class Location:
    def __init__(self, rack: str, shelf: str):
        self.rack: str = rack
        self.shelf: str = shelf

    def __str__(self) -> str:
        return f"стеллаж {self.rack}, полка {self.shelf}"


#книга (Book)
class Book:
    def __init__(self, title: str, author: Author, isbn: str, location: Location):
        self.title: str = title
        self.author: Author = author
        self.isbn: str = isbn
        self.location: Location = location
        self.is_available: bool = True
        self.current_borrower: Optional['Reader'] = None

    def __str__(self) -> str:
        status = "доступна" if self.is_available else f"выдана {self.current_borrower.first_name} {self.current_borrower.last_name}"
        return f"'{self.title}' ({self.author}) — {status}"


#читатель (Reader)
class Reader:
    def __init__(self, first_name: str, last_name: str, phone: str, email: str, reader_type: str):
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.phone: str = phone
        self.email: str = email
        self.reader_type: str = reader_type  # "school", "student", "regular"
        self.borrowed_books: List[Book] = []
        self.ticket: Ticket = Ticket(self)
        self.review: Optional['Review'] = None
        self.in_club: bool = False
        self.education_place: str = ""  #редактирует только библиотекарь

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

    def __init__(self, last_name: str, first_name: str, phone: str):
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.phone: str = phone
    
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
    def __init__(self, first_name: str, last_name: str, phone: str, email: str, school_name: str, grade: str):
        super().__init__(first_name, last_name, phone, email, "school")
        self.school_name: str = school_name
        self.grade: str = grade
        self.reader_type = "school"

#студент (Student)
class Student(Reader):
    def __init__(self, first_name: str, last_name: str, phone: str, email: str, university: str, course: int):
        super().__init__(first_name, last_name, phone, email, "student")
        self.university: str = university
        self.course: int = course
        self.reader_type = "student"


#читательный зал (Room)
class Room:
    def __init__(self, name: str, total_seats: int = 20):
        self.name: str = name
        self.seats: Dict[int, Dict[datetime, 'Reader']] = {
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


#читательский билет (Ticket)
class Ticket:
    def __init__(self, owner: 'Reader'):
        self.ticket_id: str = str(uuid.uuid4())[:8].upper()
        self.issue_date: date = datetime.now().date()
        self.expiry_date: date = self.issue_date + timedelta(days=14)
        self.owner: 'Reader' = owner

    def __str__(self) -> str:
        return f"билет №{self.ticket_id} (до {self.expiry_date})"


#отзыв (Review) 
class Review:
    def __init__(self, text: str, rating: int, author: Reader):
        if not (1 <= rating <= 5):
            raise ValueError("рейтинг от 1 до 5")
        self.text: str = text
        self.rating: int = rating
        self.author: Reader = author
        self.date: datetime = datetime.now()

    def update(self, new_text: str, new_rating: int) -> None:
        if not (1 <= new_rating <= 5):
            raise ValueError("рейтинг от 1 до 5")
        self.text = new_text
        self.rating = new_rating
        self.date = datetime.now()


#читательский клуб (Club)
class Club:
    def __init__(self):
        self.members: List[Reader] = []
        self.meetings: List[datetime] = []
        self.current_book: Optional[Book] = None

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
