from classes import (
    Author, Location, Book, Reader, Librarian,
    School, Student, Room, Ticket, Review, Club
)
# Глобальные списки
books: list[Book] = []
readers: list[Reader] = []
librarians: list[Librarian] = []
rooms: list[Room] = []
clubs: list[Club] = []

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from exceptions import (
    BookNotAvailableError
)


# Файлы находятся в той же папке
JSON_FILE = "data.json"
XML_FILE = "data.xml"


def find_book_by_isbn(isbn: str) -> Book | None:
    return next((b for b in books if b.isbn == isbn), None)


def find_reader_by_name(first: str, last: str) -> Reader | None:
    return next((r for r in readers if r.first_name == first and r.last_name == last), None)


# Загрузка из JSON

def load_from_json():
    global books, readers, librarians, rooms, clubs

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Библиотекари
    librarians = [
        Librarian(l["last_name"], l["first_name"], l["phone"])
        for l in data["librarians"]
    ]

    # Читатели
    readers = []
    reader_map = {}
    for r in data["readers"]:
        reader_type = r["reader_type"]
        if reader_type == "school":
            reader = School(
                r["first_name"], r["last_name"], r["phone"], r["email"],
                r["school_name"], r["grade"]
            )
        elif reader_type == "student":
            reader = Student(
                r["first_name"], r["last_name"], r["phone"], r["email"],
                r["university"], r["course"]
            )
        else:
            reader = Reader(r["first_name"], r["last_name"], r["phone"], r["email"], reader_type)

        reader.education_place = r.get("education_place", "")
        reader.in_club = r.get("in_club", False)

        ticket_data = r["ticket"]  
        ticket = Ticket(reader)
        ticket.ticket_id = ticket_data["ticket_id"]
        ticket.issue_date = datetime.fromisoformat(ticket_data["issue_date"]).date()
        ticket.expiry_date = datetime.fromisoformat(ticket_data["expiry_date"]).date()
        reader.ticket = ticket

        rev = r.get("review")
        if rev:
            review = Review(rev["text"], rev["rating"], reader)
            review.date = datetime.fromisoformat(rev["date"])
            reader.review = review

        full_name = f"{r['first_name']} {r['last_name']}"
        reader_map[full_name] = reader
        readers.append(reader)

    # Книги + восстановление заёмщиков
    author_cache = {}
    books = []
    for b in data["books"]:
        key = (b["author"]["first_name"], b["author"]["last_name"])
        if key not in author_cache:
            author_cache[key] = Author(
                b["author"]["first_name"],
                b["author"]["last_name"],
                b["author"].get("bio", "")
            )
        author = author_cache[key]
        location = Location(b["location"]["rack"], b["location"]["shelf"])
        book = Book(b["title"], author, b["isbn"], location)
        book.is_available = b["is_available"]

        borrower_data = b.get("current_borrower_name")
        if borrower_data and not book.is_available:
            borrower_full_name = f"{borrower_data['first_name']} {borrower_data['last_name']}"
            borrower = reader_map.get(borrower_full_name)
            if borrower:
                book.current_borrower = borrower
                borrower.borrowed_books.append(book)

        books.append(book)

    # Читальные залы
    rooms = []
    for room_data in data["rooms"]:
        room = Room(room_data["name"])
        for booking in room_data.get("bookings", []):
            try:
                dt = datetime.fromisoformat(booking["datetime"])
                seat_num = booking["seat_number"]
                # Обработка reader_name как объекта
                rn = booking.get("reader_name")
                if rn:
                    reader_full_name = f"{rn['first_name']} {rn['last_name']}"
                    reader = reader_map.get(reader_full_name)
                    if reader:
                        room.seats[seat_num][dt] = reader
            except (KeyError, ValueError) as e:
                print(f"Пропущено бронирование: {booking}")
                continue
        rooms.append(room)

    # Клубы
    clubs = []
    for club_data in data["clubs"]:
        club = Club()
        # Обработка members_names как одного участника (объект)
        member_data = club_data.get("members_names")
        if member_data:
            member_name = f"{member_data['first_name']} {member_data['last_name']}"
            member = reader_map.get(member_name)
            if member:
                club.members.append(member)
                member.in_club = True

        for dt_str in club_data.get("meetings", []):
            club.meetings.append(datetime.fromisoformat(dt_str))
        
        isbn = club_data.get("current_book_isbn")
        if isbn:
            book = find_book_by_isbn(isbn)
            if book:
                club.current_book = book
        clubs.append(club)

def load_from_xml():
    global books, readers, librarians, rooms, clubs

    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    # Библиотекари
    librarians = []
    for lib in root.find("Librarians"):
        first = lib.find("FirstName").text
        last = lib.find("LastName").text
        phone = lib.find("Phone").text
        librarians.append(Librarian(last, first, phone))

    # Собираем авторов и книги
    author_cache = {}
    books = []
    reader_map = {}

    # Сначала читаем всех читателей, чтобы потом связать книги
    readers = []
    for reader_el in root.find("Readers"):
        r_type = reader_el.get("ReaderType", "regular")
        first = reader_el.find("FirstName").text
        last = reader_el.find("LastName").text
        phone = reader_el.find("Phone").text
        email = reader_el.find("Email").text

        if r_type == "school":
            school_name = reader_el.find("SchoolName").text
            grade = reader_el.find("Grade").text
            reader = School(first, last, phone, email, school_name, grade)
        elif r_type == "student":
            university = reader_el.find("University").text
            course = int(reader_el.find("Course").text)
            reader = Student(first, last, phone, email, university, course)
        else:
            reader = Reader(first, last, phone, email, r_type)

        reader.education_place = reader_el.find("EducationPlace").text
        reader.in_club = reader_el.find("InClub").text.lower() == "true"

        # Билет
        ticket_el = reader_el.find("Ticket")
        ticket = Ticket(reader)
        ticket.ticket_id = ticket_el.find("TicketId").text
        ticket.issue_date = datetime.fromisoformat(ticket_el.find("IssueDate").text).date()
        ticket.expiry_date = datetime.fromisoformat(ticket_el.find("ExpiryDate").text).date()
        reader.ticket = ticket

        # Отзыв
        review_el = reader_el.find("Review")
        if review_el is not None and review_el.find("Text") is not None:
            text = review_el.find("Text").text or ""
            rating = int(review_el.find("Rating").text)
            date_str = review_el.find("Date").text
            if text and rating and date_str:
                review = Review(text, rating, reader)
                review.date = datetime.fromisoformat(date_str)
                reader.review = review

        full_name = f"{first} {last}"
        reader_map[full_name] = reader
        readers.append(reader)

    # Теперь книги
    for book_el in root.find("Books"):
        title = book_el.find("Title").text
        author_el = book_el.find("Author")
        author_key = (author_el.find("FirstName").text, author_el.find("LastName").text)
        if author_key not in author_cache:
            bio = author_el.find("Bio").text or ""
            author_cache[author_key] = Author(*author_key, bio)
        author = author_cache[author_key]

        isbn = book_el.find("ISBN").text
        loc_el = book_el.find("Location")
        location = Location(loc_el.find("Rack").text, loc_el.find("Shelf").text)
        is_avail = book_el.find("IsAvailable").text.lower() == "true"

        book = Book(title, author, isbn, location)
        book.is_available = is_avail

        curr_borrower_el = book_el.find("CurrentBorrower")
        if curr_borrower_el is not None and curr_borrower_el.text:
            borrower_name = curr_borrower_el.text
            borrower = reader_map.get(borrower_name)
            if borrower:
                book.current_borrower = borrower
                borrower.borrowed_books.append(book)

        books.append(book)

    # Читальные залы
    rooms = []
    for room_el in root.find("Rooms"):
        name = room_el.find("Name").text
        room = Room(name)
        bookings_el = room_el.find("Bookings")
        if bookings_el is not None:
            for booking in bookings_el:
                seat_num = int(booking.find("SeatNumber").text)
                dt = datetime.fromisoformat(booking.find("Datetime").text)
                reader_name = booking.find("Reader").text
                reader = reader_map.get(reader_name)
                if reader:
                    room.seats[seat_num][dt] = reader
        rooms.append(room)

    # Клубы
    clubs = []
    for club_el in root.find("Clubs"):
        club = Club()
        members_el = club_el.find("Members")
        if members_el is not None:
            for member_el in members_el:
                name = member_el.text
                member = reader_map.get(name)
                if member:
                    club.members.append(member)
                    member.in_club = True

        meetings_el = club_el.find("Meetings")
        if meetings_el is not None:
            for meeting_el in meetings_el:
                dt = datetime.fromisoformat(meeting_el.text)
                club.meetings.append(dt)

        isbn_el = club_el.find("CurrentBookIsbn")
        if isbn_el is not None and isbn_el.text:
            book = find_book_by_isbn(isbn_el.text)
            if book:
                club.current_book = book

        clubs.append(club)

# Сохранение в JSON и XML

def save_data():
    save_to_json()
    save_to_xml()


def save_to_json():
    data = {
        "librarians": [
            {"first_name": l.first_name, "last_name": l.last_name, "phone": l.phone}
            for l in librarians
        ],
        "readers": [],
        "books": [],
        "rooms": [],
        "clubs": []
    }

    for r in readers:
        rd = {
            "first_name": r.first_name,
            "last_name": r.last_name,
            "phone": r.phone,
            "email": r.email,
            "reader_type": r.reader_type,
            "education_place": r.education_place,
            "in_club": r.in_club,
            "borrowed_books_isbn": [b.isbn for b in r.borrowed_books],
            "ticket": {
                "ticket_id": r.ticket.ticket_id,
                "issue_date": r.ticket.issue_date.isoformat(),
                "expiry_date": r.ticket.expiry_date.isoformat()
            }
        }
        if r.reader_type == "school":
            rd["school_name"] = r.school_name
            rd["grade"] = r.grade
        elif r.reader_type == "student":
            rd["university"] = r.university
            rd["course"] = r.course

        if r.review:
            rd["review"] = {
                "text": r.review.text,
                "rating": r.review.rating,
                "date": r.review.date.isoformat()
            }
        else:
            rd["review"] = None

        data["readers"].append(rd)

    for b in books:
        data["books"].append({
            "title": b.title,
            "author": {
                "first_name": b.author.first_name,
                "last_name": b.author.last_name,
                "bio": b.author.bio
            },
            "isbn": b.isbn,
            "location": {"rack": b.location.rack, "shelf": b.location.shelf},
            "is_available": b.is_available,
            "current_borrower": (
                f"{b.current_borrower.first_name} {b.current_borrower.last_name}"
                if b.current_borrower else None
            )
        })

    for room in rooms:
        bookings = []
        for seat_num, times in room.seats.items():
            for dt, reader in times.items():
                bookings.append({
                    "seat_number": seat_num,
                    "datetime": dt.isoformat(),
                    "reader": f"{reader.first_name} {reader.last_name}"
                })
        data["rooms"].append({"name": room.name, "bookings": bookings})

    for club in clubs:
        data["clubs"].append({
            "members": [f"{m.first_name} {m.last_name}" for m in club.members],
            "meetings": [dt.isoformat() for dt in club.meetings],
            "current_book_isbn": club.current_book.isbn if club.current_book else None
        })

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_to_xml():
    root = ET.Element("Library")

    # Librarians
    lib_el = ET.SubElement(root, "Librarians")
    for l in librarians:
        el = ET.SubElement(lib_el, "Librarian")
        ET.SubElement(el, "FirstName").text = l.first_name
        ET.SubElement(el, "LastName").text = l.last_name
        ET.SubElement(el, "Phone").text = l.phone

    # Books
    books_el = ET.SubElement(root, "Books")
    for b in books:
        book = ET.SubElement(books_el, "Book")
        ET.SubElement(book, "Title").text = b.title
        auth = ET.SubElement(book, "Author")
        ET.SubElement(auth, "FirstName").text = b.author.first_name
        ET.SubElement(auth, "LastName").text = b.author.last_name
        ET.SubElement(auth, "Bio").text = b.author.bio
        ET.SubElement(book, "ISBN").text = b.isbn
        loc = ET.SubElement(book, "Location")
        ET.SubElement(loc, "Rack").text = b.location.rack
        ET.SubElement(loc, "Shelf").text = b.location.shelf
        ET.SubElement(book, "IsAvailable").text = str(b.is_available)
        if b.current_borrower:
            ET.SubElement(book, "CurrentBorrower").text = f"{b.current_borrower.first_name} {b.current_borrower.last_name}"

    # Readers
    readers_el = ET.SubElement(root, "Readers")
    for r in readers:
        reader = ET.SubElement(readers_el, "Reader", type=r.reader_type)
        ET.SubElement(reader, "FirstName").text = r.first_name
        ET.SubElement(reader, "LastName").text = r.last_name
        ET.SubElement(reader, "Phone").text = r.phone
        ET.SubElement(reader, "Email").text = r.email
        ET.SubElement(reader, "EducationPlace").text = r.education_place
        ET.SubElement(reader, "InClub").text = str(r.in_club)

        if r.reader_type == "school":
            ET.SubElement(reader, "SchoolName").text = r.school_name
            ET.SubElement(reader, "Grade").text = r.grade
        elif r.reader_type == "student":
            ET.SubElement(reader, "University").text = r.university
            ET.SubElement(reader, "Course").text = str(r.course)

        ticket = ET.SubElement(reader, "Ticket")
        ET.SubElement(ticket, "TicketId").text = r.ticket.ticket_id
        ET.SubElement(ticket, "IssueDate").text = r.ticket.issue_date.isoformat()
        ET.SubElement(ticket, "ExpiryDate").text = r.ticket.expiry_date.isoformat()

        if r.review:
            rev = ET.SubElement(reader, "Review")
            ET.SubElement(rev, "Text").text = r.review.text
            ET.SubElement(rev, "Rating").text = str(r.review.rating)
            ET.SubElement(rev, "Date").text = r.review.date.isoformat()

        borrowed = ET.SubElement(reader, "BorrowedBooks")
        for book in r.borrowed_books:
            ET.SubElement(borrowed, "ISBN").text = book.isbn

    # Rooms
    rooms_el = ET.SubElement(root, "Rooms")
    for room in rooms:
        r_el = ET.SubElement(rooms_el, "Room")
        ET.SubElement(r_el, "Name").text = room.name
        bookings = ET.SubElement(r_el, "Bookings")
        for seat, times in room.seats.items():
            for dt, reader in times.items():
                b = ET.SubElement(bookings, "Booking")
                ET.SubElement(b, "SeatNumber").text = str(seat)
                ET.SubElement(b, "DateTime").text = dt.isoformat()
                ET.SubElement(b, "Reader").text = f"{reader.first_name} {reader.last_name}"

    # Clubs
    clubs_el = ET.SubElement(root, "Clubs")
    for club in clubs:
        c = ET.SubElement(clubs_el, "Club")
        members = ET.SubElement(c, "Members")
        for m in club.members:
            ET.SubElement(members, "Member").text = f"{m.first_name} {m.last_name}"
        meetings = ET.SubElement(c, "Meetings")
        for dt in club.meetings:
            ET.SubElement(meetings, "Meeting").text = dt.isoformat()
        if club.current_book:
            ET.SubElement(c, "CurrentBookISBN").text = club.current_book.isbn

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

# Рабочая область (мб меню)?

def reader_menu(reader: Reader):
    while True:
        print("\n=== Личный кабинет читателя ===")
        print("1. Взять книгу")
        print("2. Вернуть книгу")
        print("3. Написать/изменить отзыв")
        print("4. Забронировать место в читальном зале")
        print("5. Читательский клуб")
        print("6. Изменить данные профиля")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            isbn = input("Введите ISBN книги: ").strip()
            book = find_book_by_isbn(isbn)
            if book:
                try:
                    success = reader.take_book(book)
                    if success:
                        print("Книга успешно взята!")
                except BookNotAvailableError as e: 
                    print(f"Ошибка: {e}")
            else:
                print(f"Книга с ISBN '{isbn}' не найдена.")

        elif choice == "2":
            if not reader.borrowed_books:
                print("У вас нет взятых книг.")
                continue
            print("Ваши книги:")
            for i, b in enumerate(reader.borrowed_books, 1):
                print(f"{i}. {b}")
            try:
                idx = int(input("Номер книги для возврата: ")) - 1
                if 0 <= idx < len(reader.borrowed_books):
                    book = reader.borrowed_books[idx]
                    reader.return_borrowed_book(book)
                    print("Книга возвращена.")
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Введите число.")

        elif choice == "3":
            text = input("Текст отзыва: ").strip()
            try:
                rating = int(input("Оценка (1–5): "))
                reader.set_review(text, rating)
                print("Отзыв сохранён.")
            except (ValueError, TypeError) as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            if not rooms:
                print("Нет читальных залов.")
                continue
            room = rooms[0]
            try:
                seat = int(input(f"Место (1–{len(room.seats)}): "))
                hour = int(input("Час (9–20): "))
                dt = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
                if room.reserve_seat(seat, dt, reader):
                    print(f"Место №{seat} забронировано на {dt.strftime('%d.%m %H:%M')}")
                else:
                    print("Место занято.")
            except ValueError:
                print("Неверный ввод.")

        elif choice == "5":
            club = clubs[0] if clubs else None
            if not club:
                print("Клуб не настроен.")
                continue
            if reader in club.members:
                print("Вы участник клуба.")
                if club.current_book:
                    print(f"Обсуждаемая книга: {club.current_book}")
                print("Встречи:", [d.strftime("%d.%m %H:%M") for d in club.meetings])
                if input("Покинуть клуб? (y/n): ").lower() == "y":
                    club.leave(reader)
            else:
                if input("Вступить в клуб? (y/n): ").lower() == "y":
                    club.join(reader)
                    print("Добро пожаловать!")

        elif choice == "6":
            print("Место учёбы/работы (только библиотекарь может изменить):", reader.education_place)

        elif choice == "0":
            break


def librarian_menu(librarian: Librarian):
    while True:
        print("\n=== Кабинет библиотекаря ===")
        print("1. Выдать книгу")
        print("2. Принять возврат")
        print("3. Изменить место учёбы читателя")
        print("4. Список читателей")
        print("5. Добавить новую книгу")
        print("6. Изменить местоположение книги")
        print("7. Удалить книгу")
        print("8. Зарегистрировать нового читателя")
        print("9. Удалить читателя")
        print("0. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            isbn = input("ISBN: ")
            first = input("Имя читателя: ")
            last = input("Фамилия: ")
            book = find_book_by_isbn(isbn)
            reader = find_reader_by_name(first, last)
            if book and reader:
                if librarian.lend_book_to_reader(book, reader):
                    print("Книга выдана.")
                else:
                    print("Не удалось выдать.")
            else:
                print("Книга или читатель не найдены.")

        elif choice == "2":
            isbn = input("ISBN: ")
            first = input("Имя: ")
            last = input("Фамилия: ")
            book = find_book_by_isbn(isbn)
            reader = find_reader_by_name(first, last)
            if book and reader:
                if librarian.accept_book_return(book, reader):
                    print("Книга принята.")
                else:
                    print("Ошибка при приёме.")
            else:
                print("Не найдено.")

        elif choice == "3":
            first = input("Имя: ")
            last = input("Фамилия: ")
            reader = find_reader_by_name(first, last)
            if reader:
                new_place = input("Новое место: ")
                librarian.edit_reader_education(reader, new_place)
                print("Обновлено.")
            else:
                print("Читатель не найден.")

        elif choice == "4":
            for r in readers:
                status = "в клубе" if r.in_club else "не в клубе"
                print(f"- {r} | {r.education_place} | {status} | книг: {len(r.borrowed_books)}")

        elif choice == "5":  # Добавить книгу
            try:
                title = input("Название книги: ").strip()
                author_first = input("Имя автора: ").strip()
                author_last = input("Фамилия автора: ").strip()
                isbn = input("ISBN (уникальный): ").strip()
                rack = input("Стеллаж: ").strip()
                shelf = input("Полка: ").strip()

                if find_book_by_isbn(isbn):
                    print("Книга с таким ISBN уже существует!")
                else:
                    author = Author(author_first, author_last)
                    location = Location(rack, shelf)
                    new_book = Book(title, author, isbn, location)
                    books.append(new_book)
                    print("Книга успешно добавлена!")
            except (ValueError, TypeError) as e:
                print(f"Ошибка при добавлении книги: {e}")

        elif choice == "6":  # Изменить местоположение книги
            isbn = input("ISBN книги: ").strip()
            book = find_book_by_isbn(isbn)
            if book:
                print(f"Текущее местоположение: {book.location}")
                rack = input("Новый стеллаж: ").strip()
                shelf = input("Новая полка: ").strip()
                book.location = Location(rack, shelf)
                print("Местоположение обновлено.")
            else:
                print("Книга не найдена.")

        elif choice == "7":  # Удалить книгу
            isbn = input("ISBN книги для удаления: ").strip()
            book = find_book_by_isbn(isbn)
            if book:
                if book.is_available:
                    books.remove(book)
                    print("Книга удалена из каталога.")
                else:
                    print("Нельзя удалить: книга сейчас выдана читателю.")
            else:
                print("Книга не найдена.")

        elif choice == "8":  # Зарегистрировать читателя
            print("Тип читателя:")
            print("1. Школьник")
            print("2. Студент")
            print("3. Обычный читатель")
            type_choice = input("Выберите тип (1/2/3): ").strip()
            first = input("Имя: ").strip()
            last = input("Фамилия: ").strip()
            phone = input("Телефон (+7XXXXXXXXXX): ").strip()
            email = input("Email: ").strip()

            try:
                if type_choice == "1":
                    school = input("Название школы: ").strip()
                    grade = input("Класс: ").strip()
                    new_reader = School(first, last, phone, email, school, grade)
                elif type_choice == "2":
                    university = input("ВУЗ: ").strip()
                    course = int(input("Курс (1-6): ").strip())
                    new_reader = Student(first, last, phone, email, university, course)
                elif type_choice == "3":
                    new_reader = Reader(first, last, phone, email, "regular")
                else:
                    print("Неверный тип.")
                    continue

                readers.append(new_reader)
                print(f"Читатель {new_reader} успешно зарегистрирован!")

            except (ValueError, TypeError) as e:
                print(f"Ошибка при создании читателя: {e}")

        elif choice == "9":  # Удалить читателя
            first = input("Имя читателя: ").strip()
            last = input("Фамилия: ").strip()
            reader = find_reader_by_name(first, last)
            if reader:
                if len(reader.borrowed_books) == 0:
                    readers.remove(reader)
                    print("Читатель удалён из системы.")
                else:
                    print("Нельзя удалить: читатель не вернул все книги.")
            else:
                print("Читатель не найден.")

        elif choice == "0":
            break

# Запуск программы

def main():
    print("Выберите формат для загрузки данных:")
    print("1. JSON (data.json)")
    print("2. XML (data.xml)")
    choice = input("Ваш выбор (1 или 2): ").strip()

    if choice == "1":
        try:
            print("Загрузка данных из data.json...")
            load_from_json()
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")
            return
    elif choice == "2":
        print("Загрузка данных из data.xml...")
        load_from_xml()
    else:
        print("Ошибка загрузки XML. Загружаем из JSON")
        load_from_json()

    # Основное меню
    while True:
        print("\n=== Библиотека ===")
        print("1. Войти как библиотекарь")
        print("2. Войти как читатель")
        print("0. Сохранить и выйти")
        print("9. Выйти без сохранения")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            try:
                code = int(input("Код доступа: "))
                if Librarian.verify_code(code):
                    librarian_menu(librarians[0])
                else:
                    print("Неверный код!")
            except (ValueError, IndexError):
                print("Ошибка: неверный ввод!")

        elif choice == "2":
            first = input("Имя: ").strip()
            last = input("Фамилия: ").strip()
            reader = find_reader_by_name(first, last)
            if reader:
                reader_menu(reader)
            else:
                print("Читатель не найден.")

        elif choice == "0":
            print("Сохранение данных в data.json и data.xml...")
            save_data()
            print("Данные сохранены. До свидания!")
            break

        elif choice == "9":
            confirm = input("Вы уверены, что хотите выйти без сохранения? (y/n): ").strip().lower()
            if confirm == "y":
                print("Выход без сохранения. Все изменения отменены.")
                break
            else:
                print("Продолжаем работу.")

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()