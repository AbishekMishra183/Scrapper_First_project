import requests
import sqlite3
import json
import csv
from bs4 import BeautifulSoup
from tabulate import tabulate  # For pretty table display

URL = "http://books.toscrape.com/"

# Step 1: Create the books table in SQLite
def create_table():
    con = sqlite3.connect("books.sqlite3")
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            currency TEXT,
            price REAL
        );
        """
    )
    con.commit()
    con.close()

# Step 2: Insert a book record into the table
def insert_book(title, currency, price):
    conn = sqlite3.connect("books.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
        (title, currency, price)
    )
    conn.commit()
    conn.close()

# Step 3: Scrape books from the website
def scrape_books(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch webpage.")
        return []

    books = []
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all("article", class_="product_pod")

    for book in book_elements:
        title = book.h3.a['title']
        price_text = book.find("p", class_="price_color").text
        currency = price_text[0]
        price = float(price_text[1:])

        books.append({
            "title": title,
            "currency": currency,
            "price": price
        })

        insert_book(title, currency, price)

    print("All books have been scraped and saved to the database.")
    return books

# Step 4: Save books to a JSON file
def save_to_json(books):
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)
    print("Books have been saved to books.json")

# Step 5: Save books to a CSV file
def save_to_csv(books):
    with open("books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "currency", "price"])
        writer.writeheader()
        writer.writerows(books)
    print("Books have been saved to books.csv")

# Step 6: Import books from CSV into SQLite (optional)
def import_csv_to_db(csv_file):
    conn = sqlite3.connect("books.sqlite3")
    cursor = conn.cursor()

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["title"]
            currency = row["currency"]
            price = float(row["price"])
            cursor.execute(
                "INSERT INTO books (title, currency, price) VALUES (?, ?, ?)",
                (title, currency, price)
            )

    conn.commit()
    conn.close()
    print(f"CSV file '{csv_file}' successfully imported into the database.")

# Step 7: Display books in tabular format
def display_books():
    conn = sqlite3.connect("books.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    print("\n📚 Books in Database:\n")
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    conn.close()

# Main execution
if __name__ == "__main__":
    create_table()
    books = scrape_books(URL)
    save_to_json(books)
    save_to_csv(books)
    # import_csv_to_db("books.csv")  # Optional
    display_books()
