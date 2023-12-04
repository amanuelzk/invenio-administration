from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import update
# Database configuration
host = "localhost"
user = "root"
password = ""
database = "file_storage"

# Connection string for MySQL
connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

# Create the engine and establish the connection
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class OriginalFile(Base):
    __tablename__ = 'original_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)
    file_type = Column(String(255))
    metadata_file = Column(JSON)
    file_size = Column(Integer)
    publish_status = Column(String(255))
    searchability = Column(LONGTEXT)
    project_status = Column(String(255))
# Assuming 'File' refers to the 'file' table and 'id' refers to the primary key of 'file' table
class EnglishFile(Base):
    __tablename__ = 'english_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
# Assuming 'File' refers to the 'file' table and 'id' refers to the primary key of 'file' table
class FrenchFile(Base):
    __tablename__ = 'french_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
# Assuming 'File' refers to the 'file' table and 'id' refers to the primary key of 'file' table
class SpanishFile(Base):
    __tablename__ = 'spanish_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
class ArabicFile(Base):
  __tablename__ = 'arabic_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(LargeBinary)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
class EnglishMetadata(Base):
    __tablename__ = 'english_metadata'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(JSON)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
class FrenchMetadata(Base):
    __tablename__ = 'french_metadata'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(JSON)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
class ArabicMetadata(Base):
    __tablename__ = 'arabic_metadata'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(JSON)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])

class SpanishMetadata(Base):
    __tablename__ = 'spanish_metadata'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    file_data = Column(JSON)
    file_type = Column(String(255))
    file_size = Column(Integer)
    project_pass = Column(String(255))
    project_id = Column(String(255))
    project_status = Column(String(255))
    job_status = Column(String(255))
    download_status = Column(String(255))
    upload_status = Column(String(255))
    original_file_id = Column(Integer, ForeignKey('original_file.id'))
    original_file = relationship("OriginalFile", foreign_keys=[original_file_id])
