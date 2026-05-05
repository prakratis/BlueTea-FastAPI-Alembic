from sqlalchemy import Column, Integer, String, DateTime ,LargeBinary
from datetime import datetime, timezone 
from database import Base


class SecretMessage(Base):
    __tablename__ = "messages"
   
    id = Column(Integer, primary_key=True, index=True)
    # CHANGE: Use LargeBinary to store encrypted bytes
    #content = Column(String, nullable=False)
    #author = Column(String, default="Anonymous")
    content = Column(LargeBinary) 
    author = Column(String)
    
    # Stores the CSS class: 'card-denim', 'card-ribbon', or 'card-archive'
    #card_type = Column(String, nullable=False)
    card_type = Column(String)
    
    # Tracks when the confession was made
    #timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # ADD: Timestamp for TTL (Self-destruct) logic
    #created_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))