from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, select
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "task_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50))
    input_content = Column(Text)
    agent_used = Column(String(50))
    output_content = Column(Text)
    metadata_json = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ContextStore:
    def __init__(self, db_path="sqlite:///data/context.db"):
        self.engine = create_engine(db_path, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_record(self, task_type, input_content, agent_used, output_content, metadata=None):
        session = self.Session()
        metadata_json = json.dumps(metadata) if metadata else "{}"

        record = TaskRecord(
            task_type=task_type,
            input_content=input_content,
            agent_used=agent_used,
            output_content=output_content,
            metadata_json=metadata_json
        )
        session.add(record)
        session.commit()
        session.close()

    def get_last_records(self, limit=10):
        session = self.Session()
        records = session.query(TaskRecord).order_by(TaskRecord.id.desc()).limit(limit).all()
        # records = session.execute(select(TaskRecord)).scalars().all()
        session.close()
        return records
