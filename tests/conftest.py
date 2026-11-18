import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import chromadb
from backend.app.database.session import Base, get_db
from backend.app.database.fts_index import init_fts_table, index_product_fts
from backend.app.models.product import ProductCategory, Product, ProductSpecification
from backend.app.models.user import User
from backend.app.main import app

@pytest.fixture(scope="session")
def test_db_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Provide a transactional in-memory database session for each test function."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    # Initialize FTS5 and categories
    init_fts_table(session)
    if session.query(ProductCategory).count() == 0:
        session.add(ProductCategory(name="Laptops", slug="laptops", description="Laptops"))
        session.add(ProductCategory(name="Headphones", slug="headphones", description="Headphones"))
        session.add(ProductCategory(name="Monitors", slug="monitors", description="Monitors"))
        session.add(ProductCategory(name="Smartphones", slug="smartphones", description="Smartphones"))
        session.add(User(id="default_user", username="Test User"))
        session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    """FastAPI TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
