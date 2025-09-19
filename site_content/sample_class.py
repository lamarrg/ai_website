from sqlalchemy import Column, Integer, String, Text
from database import Base

class SampleClass(Base):
    __tablename__ = 'sample_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    def __init__(self, name: str, description: str = "", url: str = "") -> None:
        self.name = name
        self.description = description
        self.url = url

    def __repr__(self) -> str:
        return f"<SampleClass(id={self.id}, name='{self.name}', url='{self.url}', description='{self.description}')>"
