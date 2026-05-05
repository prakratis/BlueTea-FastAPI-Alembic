from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone  # Combined and updated

from cryptography.fernet import Fernet
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request


# Import our custom database and model logic
import models
from database import engine, get_db

# Initialize the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. Encryption Setup (Use the key you generated in PowerShell)
# In production, this would be in an environment variable
SECRET_KEY = b'1BWt30WXAqjC6AoAn-inJR8EErq4DvfXTN6v2woygGU='
cipher = Fernet(SECRET_KEY)

# 2. Rate Limiter Setup (Prevents Spam)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Mount the static folder (CSS/JS)
app.mount("/ui", StaticFiles(directory="static"), name="static")

# 2. Serve the frontend at the root
@app.get("/")
def read_index():
    return FileResponse("static/index.html")

# 3. GET all messages from the Database
@app.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    # ADD: Calculate the 24-hour cutoff
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

    # Query SQLAlchemy instead of a local list
    #messages = db.query(models.SecretMessage).order_by(models.SecretMessage.id.desc()).all()
    #return messages

    messages = db.query(models.SecretMessage)\
                 .filter(models.SecretMessage.created_at >= time_threshold)\
                 .order_by(models.SecretMessage.id.desc()).all()
    
    # ADD: Decrypt each message for the UI
    decrypted_list = []
    for msg in messages:
        try:
            readable_text = cipher.decrypt(msg.content).decode()
            decrypted_list.append({
                "id": msg.id,
                "author": msg.author,
                "card_type": msg.card_type,
                "content": readable_text
            })
        except Exception:
            continue # Skip if decryption fails
            
    return decrypted_list
    

# 4. POST a new secret to the Database
@app.post("/messages")
def create_message(
    text: str, 
    type: str, 
    name: Optional[str] = "Anonymous", 
    db: Session = Depends(get_db)
):
    # Validation logic
    if not text.strip():
        raise HTTPException(status_code=400, detail="Cutie, you can't post an empty message!")
    
    if len(text) > 200:
        raise HTTPException(status_code=400, detail="Message is too long! Keep it under 200 characters.")
    
    # ADD: Encrypt the text before saving
    encrypted_text = cipher.encrypt(text.encode())

    # Create the database object
    new_msg = models.SecretMessage(
        #content=text,
        content=encrypted_text, # CHANGE: Save the encrypted bytes, not plain text
        author=name,
        card_type=type  # This maps to 'card-denim', 'card-ribbon', etc.
    )

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    #return new_msg
    return {"status": "Secret encrypted and saved!"}

# 5. SEARCH secrets
@app.get("/search")
def search_message(keyword: str, db: Session = Depends(get_db)):
    """
    results = db.query(models.SecretMessage).filter(
        models.SecretMessage.content.contains(keyword)
    ).all()
    return results 
    """

    # ADD: Define the cutoff time (24 hours ago)
    #time_threshold = datetime.utcnow() - timedelta(hours=24)
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # UPDATE: Only query messages created within the last 24 hours
    messages = db.query(models.SecretMessage)\
                 .filter(models.SecretMessage.created_at >= time_threshold)\
                 .order_by(models.SecretMessage.id.desc()).all()
    
    # ADD: Decrypt each message for the frontend
    decrypted_messages = []
    for msg in messages:
        try:
            decrypted_text = cipher.decrypt(msg.content).decode()
            decrypted_messages.append({
                "id": msg.id,
                "author": msg.author,
                "card_type": msg.card_type,
                "content": decrypted_text
            })
        except Exception:
            continue # Skip messages that can't be decrypted

    return decrypted_messages
    