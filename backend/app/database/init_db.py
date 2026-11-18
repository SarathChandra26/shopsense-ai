from sqlalchemy.orm import Session
from backend.app.database.session import engine, SessionLocal, Base
from backend.app.models.product import ProductCategory
from backend.app.models.user import User
from backend.app.database.fts_index import init_fts_table
from backend.app.core.logging import logger

DEFAULT_CATEGORIES = [
    ("Laptops", "laptops", "High-performance, ultrabook, and gaming portable computers"),
    ("Smartphones", "smartphones", "Modern 5G smartphones, flagship and budget mobile devices"),
    ("Headphones", "headphones", "Wireless, over-ear, noise-cancelling, and audiophile headphones"),
    ("Smartwatches", "smartwatches", "Fitness trackers, cellular, and health monitoring wearables"),
    ("Monitors", "monitors", "4K, high-refresh gaming, IPS, and professional productivity displays"),
    ("Keyboards", "keyboards", "Mechanical, ergonomic, wireless, and low-profile computer keyboards"),
    ("Mice", "mice", "Ergonomic, lightweight gaming, and wireless productivity mice"),
    ("Tablets", "tablets", "Productivity, digital art, student, and multimedia tablet computers"),
    ("Gaming Accessories", "gaming-accessories", "Controllers, headsets, gaming mousepads, and capture cards"),
    ("Storage Devices", "storage-devices", "NVMe SSDs, external backup drives, and high-speed flash drives"),
]

def init_db(db: Session = None) -> None:
    """Initialize database tables, default categories, and default user."""
    # Create all SQLAlchemy tables
    Base.metadata.create_all(bind=engine)
    
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Initialize FTS5 index table
        init_fts_table(db)

        # Seed categories if empty
        existing_count = db.query(ProductCategory).count()
        if existing_count == 0:
            logger.info("Seeding default product categories...")
            for name, slug, desc in DEFAULT_CATEGORIES:
                cat = ProductCategory(name=name, slug=slug, description=desc)
                db.add(cat)
            db.commit()
            logger.info(f"Seeded {len(DEFAULT_CATEGORIES)} product categories.")

        # Seed default user if not present
        default_user = db.query(User).filter(User.id == "default_user").first()
        if not default_user:
            default_user = User(id="default_user", username="ShopSense Explorer")
            db.add(default_user)
            db.commit()
            logger.info("Initialized default user session: 'default_user'")
    finally:
        if close_session:
            db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
