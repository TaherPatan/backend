import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.src.database import Base, get_db
from backend.src import crud, models, schemas
from backend.src.auth import get_password_hash, verify_password

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Fixture to provide a test database session
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test cases for CRUD operations
def test_create_user(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    db_user = crud.create_user(db=test_db, user=user_data)
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert hasattr(db_user, "hashed_password")
    assert db_user.role == "viewer"

def test_get_user(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    retrieved_user = crud.get_user(db=test_db, user_id=created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"

def test_get_user_by_username(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    crud.create_user(db=test_db, user=user_data)
    retrieved_user = crud.get_user_by_username(db=test_db, username="testuser")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"

def test_get_user_by_email(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    crud.create_user(db=test_db, user=user_data)
    retrieved_user = crud.get_user_by_email(db=test_db, email="test@example.com")
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

def test_get_users(test_db):
    user_data1 = schemas.UserCreate(username="testuser1", email="test1@example.com", password="password123", role="viewer")
    user_data2 = schemas.UserCreate(username="testuser2", email="test2@example.com", password="password456", role="editor")
    crud.create_user(db=test_db, user=user_data1)
    crud.create_user(db=test_db, user=user_data2)
    users = crud.get_users(db=test_db)
    assert len(users) == 2

def test_update_user_role(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    updated_user = crud.update_user_role(db=test_db, user_id=created_user.id, role="admin")
    assert updated_user is not None
    assert updated_user.role == "admin"

def test_delete_user(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    deleted_user = crud.delete_user(db=test_db, user_id=created_user.id)
    assert deleted_user is not None
    retrieved_user = crud.get_user(db=test_db, user_id=created_user.id)
    assert retrieved_user is None

def test_create_document(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    document_data = schemas.DocumentCreate(title="Test Document")
    db_document = crud.create_document(db=test_db, document=document_data, owner_id=created_user.id, filename="test_document.txt")
    assert db_document.title == "Test Document"
    assert db_document.filename == "test_document.txt"
    assert db_document.owner_id == created_user.id

def test_get_document(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    document_data = schemas.DocumentCreate(title="Test Document")
    created_document = crud.create_document(db=test_db, document=document_data, owner_id=created_user.id, filename="test_document.txt")
    retrieved_document = crud.get_document(db=test_db, document_id=created_document.id)
    assert retrieved_document is not None
    assert retrieved_document.title == "Test Document"

def test_get_documents(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    document_data1 = schemas.DocumentCreate(title="Test Document 1")
    document_data2 = schemas.DocumentCreate(title="Test Document 2")
    crud.create_document(db=test_db, document=document_data1, owner_id=created_user.id, filename="test_document1.txt")
    crud.create_document(db=test_db, document=document_data2, owner_id=created_user.id, filename="test_document2.txt")
    documents = crud.get_documents(db=test_db)
    assert len(documents) == 2

def test_delete_document(test_db):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com", password="password123", role="viewer")
    created_user = crud.create_user(db=test_db, user=user_data)
    document_data = schemas.DocumentCreate(title="Test Document")
    created_document = crud.create_document(db=test_db, document=document_data, owner_id=created_user.id, filename="test_document.txt")
    deleted_document = crud.delete_document(db=test_db, document_id=created_document.id)
    assert deleted_document is not None
    retrieved_document = crud.get_document(db=test_db, document_id=created_document.id)
    assert retrieved_document is None

# Test cases for Authentication
def test_get_password_hash():
    password = "securepassword"
    hashed_password = get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0

def test_verify_password():
    password = "securepassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False