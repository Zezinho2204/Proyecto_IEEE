from sqlalchemy import Column, Integer, String, Float, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    email = Column(String(100))
    perfil = Column(Text)
    skills = Column(Text)
    experiencia = Column(Text)
    seniority = Column(String(50))
    area_profesional = Column(String(100))
    match = Column(Float)
    cv_text = Column(Text)

# Config DB
engine = create_engine("sqlite:///candidates.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
