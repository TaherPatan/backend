import os
import shutil

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import timedelta
import time

from . import crud, models, schemas, database
from .auth import authenticate_user, create_access_token, get_current_active_user
from .config import settings

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the directory for uploaded documents if it doesn't exist
os.makedirs(settings.documents_upload_path, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# User Management Endpoints (Admin only)
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access user list")
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.put("/users/{user_id}/role", response_model=schemas.User)
def update_user_role(user_id: int, role_update: schemas.UserRoleUpdate, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update user roles")
    db_user = crud.update_user_role(db, user_id=user_id, role=role_update.role)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete users")
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Document Management Endpoints
from fastapi import File, UploadFile

@app.post("/documents/", response_model=schemas.Document)
async def create_document(file: UploadFile = File(...), current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Save the file to the designated upload directory
    file_location = os.path.join(settings.documents_upload_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create the document entry in the database
    document_title = file.filename.split(".")[0] if "." in file.filename else file.filename
    db_document = crud.create_document(db=db, document=schemas.DocumentCreate(title=document_title), owner_id=current_user.id, filename=file.filename)

    return db_document

@app.get("/documents/", response_model=List[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # In a real application, you might want to filter documents by the current user
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents

@app.get("/documents/{document_id}", response_model=schemas.Document)
def read_document(document_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_document = crud.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    # In a real application, you might want to check if the current user has access to the document
    return db_document

@app.delete("/documents/{document_id}", response_model=schemas.Document)
def delete_document(document_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_document = crud.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    # In a real application, you might want to check if the current user is the owner or an admin
    deleted_document = crud.delete_document(db, document_id=document_id)
    return deleted_document

# In-memory storage for ingestion tasks (for demonstration purposes)
ingestion_tasks: Dict[int, schemas.IngestionTask] = {}

# Simulated ingestion process (runs in the background)
async def process_ingestion_task(document_id: int):
    """Simulates the ingestion process for a document."""
    if document_id in ingestion_tasks:
        ingestion_tasks[document_id].status = "processing"
        print(f"Starting ingestion for document ID: {document_id}")
        # Simulate work (e.g., reading file, chunking, embedding)
        time.sleep(5) # Simulate a delay
        ingestion_tasks[document_id].status = "completed"
        ingestion_tasks[document_id].message = "Ingestion completed successfully."
        print(f"Completed ingestion for document ID: {document_id}")
    else:
        print(f"Ingestion task for document ID {document_id} not found.")


# Ingestion Trigger API
@app.post("/ingest/{document_id}", response_model=schemas.IngestionTask)
async def trigger_ingestion(document_id: int, background_tasks: BackgroundTasks, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_document = crud.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if the user has permission to trigger ingestion for this document
    # For now, allow any authenticated user to trigger ingestion for any document
    # In a real app, this might be restricted to admins or document owners

    if document_id in ingestion_tasks and ingestion_tasks[document_id].status in ["pending", "processing"]:
        raise HTTPException(status_code=400, detail=f"Ingestion for document ID {document_id} is already {ingestion_tasks[document_id].status}.")

    # Create a new ingestion task entry
    ingestion_task = schemas.IngestionTask(document_id=document_id, status="pending")
    ingestion_tasks[document_id] = ingestion_task

    # Add the ingestion processing to background tasks
    background_tasks.add_task(process_ingestion_task, document_id)

    print(f"Ingestion triggered for document ID: {document_id}")
    return ingestion_task

# Ingestion Management API
@app.get("/ingestion/status", response_model=Dict[int, schemas.IngestionTask])
def get_ingestion_status(current_user: schemas.User = Depends(get_current_active_user)):
    # In a real application, this would query the status from a database
    # For this example, we return the in-memory dictionary
    return ingestion_tasks

# Endpoint to serve uploaded documents
from fastapi.responses import FileResponse

@app.get("/documents/{document_id}/download")
async def download_document(document_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_document = crud.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # In a real application, you might want to check if the current user has access to the document

    file_path = os.path.join(settings.documents_upload_path, db_document.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(path=file_path, filename=db_document.filename)

# Q&A Endpoint (Placeholder)
@app.post("/qa")
def ask_question(question_request: schemas.QuestionRequest, current_user: schemas.User = Depends(get_current_active_user)):
    # In a real application, this would:
    # 1. Use the question to query the vector database for relevant document chunks.
    # 2. Use an LLM to generate an answer based on the retrieved chunks.
    # For this example, we'll return a dummy answer.
    print(f"Received question: {question_request.question}")
    return {"answer": f"This is a placeholder answer for your question: {question_request.question}"}