from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.models import *

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    grade = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)

    user = relationship("User", backref="ratings")
    product = relationship("Product", backref="ratings")