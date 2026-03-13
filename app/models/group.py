from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Group(Base):
    __tablename__ = "posts_group"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    posts = relationship("Post", back_populates="group")
    
    def __repr__(self):
        return f"<Group(title='{self.title}')>"
