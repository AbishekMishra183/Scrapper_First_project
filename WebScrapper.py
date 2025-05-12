import requests
import sqlite3
import json
import csv
import logging
import argparse
from bs4 import BeautifulSoup
from tabulate import tabulate

# Configuration
DATABASE = "books.sqlite3"
JSON_FILE = "books.json"
CSV_FILE = "books.csv"
URL = "http://books.toscrape.com/"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("books_scraper.log"),
        logging.StreamHandler()
    ]
)

# Create table
def create_table():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                currency TEXT NOT NULL,
                price REAL NOT NULL
            );
        """)
    logging.info("Database table ready.")

# Insert book with duplicate check
def insert_book(title, currency, price):
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM books WHERE title = ? AND price = ?", (title, price))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (title, currency, price)
                )
                logging.info(f"Inserted: {title}")
            else:
                logging.info(f"Skipped duplicate: {title}")
    except sqlite3.Error as e:
        logging.error(f"Insert error: {e}")

# Scrape single page
def scrape_books(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return []

    books = []
    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        try:
            title = book.h3.a['title']
            price_text = book.find("p", class_="price_color").text
            currency = price_text[0]
            price = float(price_text[1:])

            books.append({"title": title, "currency": currency, "price": price})
            insert_book(title, currency, price)
        except Exception as e:
            logging.warning(f"Error parsing book: {e}")

    logging.info(f"Scraped {len(books)} books from {url}")
    return books

# Scrape all pages
def scrape_all_pages(base_url):
    page = 1
    all_books = []
    while True:
        page_url = f"{base_url}catalogue/page-{page}.html"
        books = scrape_books(page_url)
        if not books:
            break
        all_books.extend(books)
        page += 1
    logging.info(f"Scraping complete. Total books: {len(all_books)}")
    return all_books

# Save JSON
def save_to_json(books, filename=JSON_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"JSON save error: {e}")

# Save CSV
def save_to_csv(books, filename=CSV_FILE):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "currency", "price"])
            writer.writeheader()
            writer.writerows(books)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"CSV save error: {e}")

# Import CSV to DB
def import_csv_to_db(csv_file):
    try:
        with sqlite3.connect(DATABASE) as con, open(csv_file, "r", encoding="utf-8") as f:
            cur = con.cursor()
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (row["title"], row["currency"], float(row["price"]))
                )
        logging.info(f"Imported CSV: {csv_file}")
    except Exception as e:
        logging.error(f"CSV import error: {e}")

# Display books
def display_books():
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM books")
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            if rows:
                print("\n📚 Books in Database:\n")
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                logging.info("Database is empty.")
    except sqlite3.Error as e:
        logging.error(f"Display error: {e}")

# CLI Arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Books Scraper CLI")
    parser.add_argument("--scrape", action="store_true", help="Scrape all books")
    parser.add_argument("--display", action="store_true", help="Display all books")
    parser.add_argument("--export", action="store_true", help="Export books to JSON and CSV")
    return parser.parse_args()

# Main execution
def main():
    create_table()
    args = parse_args()

    if args.scrape:
        books = scrape_all_pages(URL)
        if args.export:
            save_to_json(books)
            save_to_csv(books)

    if args.display:
        display_books()

if __name__ == "__main__":
    main()
import requests
import sqlite3
import json
import csv
import logging
import argparse
from bs4 import BeautifulSoup
from tabulate import tabulate

# Configuration
DATABASE = "books.sqlite3"
JSON_FILE = "books.json"
CSV_FILE = "books.csv"
URL = "http://books.toscrape.com/"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("books_scraper.log"),
        logging.StreamHandler()
    ]
)

# Create table
def create_table():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                currency TEXT NOT NULL,
                price REAL NOT NULL
            );
        """)
    logging.info("Database table ready.")

# Insert book with duplicate check
def insert_book(title, currency, price):
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM books WHERE title = ? AND price = ?", (title, price))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (title, currency, price)
                )
                logging.info(f"Inserted: {title}")
            else:
                logging.info(f"Skipped duplicate: {title}")
    except sqlite3.Error as e:
        logging.error(f"Insert error: {e}")

# Scrape single page
def scrape_books(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return []

    books = []
    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        try:
            title = book.h3.a['title']
            price_text = book.find("p", class_="price_color").text
            currency = price_text[0]
            price = float(price_text[1:])

            books.append({"title": title, "currency": currency, "price": price})
            insert_book(title, currency, price)
        except Exception as e:
            logging.warning(f"Error parsing book: {e}")

    logging.info(f"Scraped {len(books)} books from {url}")
    return books

# Scrape all pages
def scrape_all_pages(base_url):
    page = 1
    all_books = []
    while True:
        page_url = f"{base_url}catalogue/page-{page}.html"
        books = scrape_books(page_url)
        if not books:
            break
        all_books.extend(books)
        page += 1
    logging.info(f"Scraping complete. Total books: {len(all_books)}")
    return all_books

# Save JSON
def save_to_json(books, filename=JSON_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"JSON save error: {e}")

# Save CSV
def save_to_csv(books, filename=CSV_FILE):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "currency", "price"])
            writer.writeheader()
            writer.writerows(books)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"CSV save error: {e}")

# Import CSV to DB
def import_csv_to_db(csv_file):
    try:
        with sqlite3.connect(DATABASE) as con, open(csv_file, "r", encoding="utf-8") as f:
            cur = con.cursor()
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (row["title"], row["currency"], float(row["price"]))
                )
        logging.info(f"Imported CSV: {csv_file}")
    except Exception as e:
        logging.error(f"CSV import error: {e}")

# Display books
def display_books():
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM books")
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            if rows:
                print("\n📚 Books in Database:\n")
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                logging.info("Database is empty.")
    except sqlite3.Error as e:
        logging.error(f"Display error: {e}")

# CLI Arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Books Scraper CLI")
    parser.add_argument("--scrape", action="store_true", help="Scrape all books")
    parser.add_argument("--display", action="store_true", help="Display all books")
    parser.add_argument("--export", action="store_true", help="Export books to JSON and CSV")
    return parser.parse_args()

# Main execution
def main():
    create_table()
    args = parse_args()

    if args.scrape:
        books = scrape_all_pages(URL)
        if args.export:
            save_to_json(books)
            save_to_csv(books)

    if args.display:
        display_books()

if __name__ == "__main__":
    main()
import requests
import sqlite3
import json
import csv
import logging
import argparse
from bs4 import BeautifulSoup
from tabulate import tabulate

# Configuration
DATABASE = "books.sqlite3"
JSON_FILE = "books.json"
CSV_FILE = "books.csv"
URL = "http://books.toscrape.com/"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("books_scraper.log"),
        logging.StreamHandler()
    ]
)

# Create table
def create_table():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                currency TEXT NOT NULL,
                price REAL NOT NULL
            );
        """)
    logging.info("Database table ready.")

# Insert book with duplicate check
def insert_book(title, currency, price):
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM books WHERE title = ? AND price = ?", (title, price))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (title, currency, price)
                )
                logging.info(f"Inserted: {title}")
            else:
                logging.info(f"Skipped duplicate: {title}")
    except sqlite3.Error as e:
        logging.error(f"Insert error: {e}")

# Scrape single page
def scrape_books(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return []

    books = []
    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        try:
            title = book.h3.a['title']
            price_text = book.find("p", class_="price_color").text
            currency = price_text[0]
            price = float(price_text[1:])

            books.append({"title": title, "currency": currency, "price": price})
            insert_book(title, currency, price)
        except Exception as e:
            logging.warning(f"Error parsing book: {e}")

    logging.info(f"Scraped {len(books)} books from {url}")
    return books

# Scrape all pages
def scrape_all_pages(base_url):
    page = 1
    all_books = []
    while True:
        page_url = f"{base_url}catalogue/page-{page}.html"
        books = scrape_books(page_url)
        if not books:
            break
        all_books.extend(books)
        page += 1
    logging.info(f"Scraping complete. Total books: {len(all_books)}")
    return all_books

# Save JSON
def save_to_json(books, filename=JSON_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"JSON save error: {e}")

# Save CSV
def save_to_csv(books, filename=CSV_FILE):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "currency", "price"])
            writer.writeheader()
            writer.writerows(books)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"CSV save error: {e}")

# Import CSV to DB
def import_csv_to_db(csv_file):
    try:
        with sqlite3.connect(DATABASE) as con, open(csv_file, "r", encoding="utf-8") as f:
            cur = con.cursor()
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (row["title"], row["currency"], float(row["price"]))
                )
        logging.info(f"Imported CSV: {csv_file}")
    except Exception as e:
        logging.error(f"CSV import error: {e}")

# Display books
def display_books():
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM books")
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            if rows:
                print("\n📚 Books in Database:\n")
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                logging.info("Database is empty.")
    except sqlite3.Error as e:
        logging.error(f"Display error: {e}")

# CLI Arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Books Scraper CLI")
    parser.add_argument("--scrape", action="store_true", help="Scrape all books")
    parser.add_argument("--display", action="store_true", help="Display all books")
    parser.add_argument("--export", action="store_true", help="Export books to JSON and CSV")
    return parser.parse_args()

# Main execution
def main():
    create_table()
    args = parse_args()

    if args.scrape:
        books = scrape_all_pages(URL)
        if args.export:
            save_to_json(books)
            save_to_csv(books)

    if args.display:
        display_books()

if __name__ == "__main__":
    main()
import requests
import sqlite3
import json
import csv
import logging
import argparse
from bs4 import BeautifulSoup
from tabulate import tabulate

# Configuration
DATABASE = "books.sqlite3"
JSON_FILE = "books.json"
CSV_FILE = "books.csv"
URL = "http://books.toscrape.com/"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("books_scraper.log"),
        logging.StreamHandler()
    ]
)

# Create table
def create_table():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                currency TEXT NOT NULL,
                price REAL NOT NULL
            );
        """)
    logging.info("Database table ready.")

# Insert book with duplicate check
def insert_book(title, currency, price):
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM books WHERE title = ? AND price = ?", (title, price))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (title, currency, price)
                )
                logging.info(f"Inserted: {title}")
            else:
                logging.info(f"Skipped duplicate: {title}")
    except sqlite3.Error as e:
        logging.error(f"Insert error: {e}")

# Scrape single page
def scrape_books(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return []

    books = []
    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        try:
            title = book.h3.a['title']
            price_text = book.find("p", class_="price_color").text
            currency = price_text[0]
            price = float(price_text[1:])

            books.append({"title": title, "currency": currency, "price": price})
            insert_book(title, currency, price)
        except Exception as e:
            logging.warning(f"Error parsing book: {e}")

    logging.info(f"Scraped {len(books)} books from {url}")
    return books

# Scrape all pages
def scrape_all_pages(base_url):
    page = 1
    all_books = []
    while True:
        page_url = f"{base_url}catalogue/page-{page}.html"
        books = scrape_books(page_url)
        if not books:
            break
        all_books.extend(books)
        page += 1
    logging.info(f"Scraping complete. Total books: {len(all_books)}")
    return all_books

# Save JSON
def save_to_json(books, filename=JSON_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"JSON save error: {e}")

# Save CSV
def save_to_csv(books, filename=CSV_FILE):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "currency", "price"])
            writer.writeheader()
            writer.writerows(books)
        logging.info(f"Saved to {filename}")
    except Exception as e:
        logging.error(f"CSV save error: {e}")

# Import CSV to DB
def import_csv_to_db(csv_file):
    try:
        with sqlite3.connect(DATABASE) as con, open(csv_file, "r", encoding="utf-8") as f:
            cur = con.cursor()
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute(
                    "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                    (row["title"], row["currency"], float(row["price"]))
                )
        logging.info(f"Imported CSV: {csv_file}")
    except Exception as e:
        logging.error(f"CSV import error: {e}")

# Display books
def display_books():
    try:
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM books")
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            if rows:
                print("\n📚 Books in Database:\n")
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                logging.info("Database is empty.")
    except sqlite3.Error as e:
        logging.error(f"Display error: {e}")

# CLI Arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Books Scraper CLI")
    parser.add_argument("--scrape", action="store_true", help="Scrape all books")
    parser.add_argument("--display", action="store_true", help="Display all books")
    parser.add_argument("--export", action="store_true", help="Export books to JSON and CSV")
    return parser.parse_args()

# Main execution
def main():
    create_table()
    args = parse_args()

    if args.scrape:
        books = scrape_all_pages(URL)
        if args.export:
            save_to_json(books)
            save_to_csv(books)

    if args.display:
        display_books()

if __name__ == "__main__":
    main()
