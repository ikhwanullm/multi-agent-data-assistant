"""Database tools and utilities."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import config


class DatabaseTool:
    """SQLite database operations."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.DATABASE_PATH
    
    def initialize_database(self):
        """Create database with sample data."""
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;
            
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                city TEXT,
                created_at DATE
            );
            
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock INTEGER
            );
            
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                total_amount REAL,
                order_date DATE,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
        """)
        
        # Sample data
        customers = [
            ("Ahmad Rizki", "ahmad.rizki@email.com", "Jakarta"),
            ("Siti Nurhaliza", "siti.nur@email.com", "Bandung"),
            ("Budi Santoso", "budi.s@email.com", "Surabaya"),
            ("Dewi Lestari", "dewi.l@email.com", "Yogyakarta"),
            ("Eko Prasetyo", "eko.p@email.com", "Semarang"),
            ("Fitri Handayani", "fitri.h@email.com", "Medan"),
            ("Gunawan Wibowo", "gunawan.w@email.com", "Makassar"),
            ("Hana Pertiwi", "hana.p@email.com", "Bali"),
            ("Irfan Hakim", "irfan.h@email.com", "Palembang"),
            ("Joko Widodo", "joko.w@email.com", "Solo"),
            ("Kartini Sari", "kartini.s@email.com", "Malang"),
            ("Lukman Hakim", "lukman.h@email.com", "Tangerang"),
            ("Maya Putri", "maya.p@email.com", "Bekasi"),
            ("Nadia Amelia", "nadia.a@email.com", "Bogor"),
            ("Oscar Putra", "oscar.p@email.com", "Depok"),
        ]
        
        products = [
            ("Laptop Gaming ASUS", "Electronics", 15000000, 50),
            ("iPhone 15 Pro", "Electronics", 20000000, 30),
            ("Samsung Galaxy S24", "Electronics", 18000000, 45),
            ("Nike Air Jordan", "Fashion", 3500000, 100),
            ("Adidas Ultraboost", "Fashion", 2800000, 80),
            ("Sony WH-1000XM5", "Electronics", 5500000, 60),
            ("iPad Pro M2", "Electronics", 17000000, 25),
            ("Uniqlo Jacket", "Fashion", 799000, 200),
            ("Mechanical Keyboard", "Electronics", 1500000, 75),
            ("Gaming Mouse Logitech", "Electronics", 1200000, 90),
            ("Smartwatch Garmin", "Electronics", 8000000, 40),
            ("Sepatu Running Asics", "Fashion", 2200000, 120),
            ("Tas Ransel Eiger", "Fashion", 850000, 150),
            ("Monitor 4K LG", "Electronics", 7500000, 35),
            ("Wireless Earbuds", "Electronics", 2500000, 110),
        ]
        
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        
        # Insert customers
        base_date = datetime.now() - timedelta(days=365)
        for i, (name, email, city) in enumerate(customers):
            created = base_date + timedelta(days=random.randint(0, 300))
            cursor.execute(
                "INSERT INTO customers (name, email, city, created_at) VALUES (?, ?, ?, ?)",
                (name, email, city, created.strftime("%Y-%m-%d"))
            )
        
        # Insert products
        for name, category, price, stock in products:
            cursor.execute(
                "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
                (name, category, price, stock)
            )
        
        # Insert orders (random distribution)
        for i in range(100):
            customer_id = random.randint(1, len(customers))
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 5)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            price = cursor.fetchone()[0]
            total = price * quantity
            
            order_date = base_date + timedelta(days=random.randint(0, 365))
            status = random.choice(statuses)
            
            cursor.execute(
                """INSERT INTO orders 
                   (customer_id, product_id, quantity, total_amount, order_date, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (customer_id, product_id, quantity, total, order_date.strftime("%Y-%m-%d"), status)
            )
        
        conn.commit()
        conn.close()
        print(f"[OK] Database initialized at {self.db_path}")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(products)} products")
        print(f"   - 100 orders")


def setup_database():
    """Initialize the database with sample data."""
    db_tool = DatabaseTool()
    db_tool.initialize_database()


if __name__ == "__main__":
    setup_database()
