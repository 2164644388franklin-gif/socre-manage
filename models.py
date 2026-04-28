from sqlalchemy import Column,Integer,String
from database import Base

class User(Base):
    __tablename__="users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    score = Column(Integer, nullable=False)

