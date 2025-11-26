import sqlalchemy as sqlch
import sqlalchemy.orm as sqlorm
from datetime import datetime
import json
import os

Base = sqlorm.declarative_base()

class PlanRecord(Base):
    __tablename__ = "plans"
    id = sqlch.Column(sqlch.Integer, primary_key=True, autoincrement=True)
    input_text = sqlch.Column(sqlch.Text)
    plan_json = sqlch.Column(sqlch.Text)  
    meta_data = sqlch.Column(sqlch.Text)  
    created_at = sqlch.Column(sqlch.DateTime, default=datetime.utcnow)

class StepRecord(Base):
    __tablename__ = "steps"
    id = sqlch.Column(sqlch.Integer, primary_key=True, autoincrement=True)
    plan_id = sqlch.Column(sqlch.Integer, sqlch.ForeignKey("plans.id"))
    step_index = sqlch.Column(sqlch.Integer)
    agent = sqlch.Column(sqlch.String(100))
    action = sqlch.Column(sqlch.String(200))   
    input_payload = sqlch.Column(sqlch.Text)
    output_payload = sqlch.Column(sqlch.Text)
    status = sqlch.Column(sqlch.String(50), default="pending") 
    meta_data = sqlch.Column(sqlch.Text)
    created_at = sqlch.Column(sqlch.DateTime, default=datetime.utcnow)

    plan = sqlorm.relationship("PlanRecord", backref="steps")

class ContextStore:
    def __init__(self, db_url=None):
        # default db in project data directory
        if db_url is None:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            db_path = os.path.join(root, "data", "context.db")
            db_url = f"sqlite:///{db_path}"

        self.engine = sqlch.create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sqlorm.sessionmaker(bind=self.engine)

    # Plans
    def save_plan(self, input_text, plan_json, meta_data=None):
        session = self.Session()
        pr = PlanRecord(
            input_text=input_text,
            plan_json=json.dumps(plan_json),
            meta_data=json.dumps(meta_data or {})
        )
        session.add(pr)
        session.commit()
        plan_id = pr.id
        session.close()
        return plan_id

    def get_plan(self, plan_id):
        session = self.Session()
        pr = session.query(PlanRecord).filter_by(id=plan_id).first()
        session.close()
        if pr is None:
            return None
        return {
            "id": pr.id,
            "input_text": pr.input_text,
            "plan_json": json.loads(pr.plan_json),
            "meta_data": json.loads(pr.meta_data),
            "created_at": pr.created_at.isoformat()
        }

    # Steps
    def add_step(self, plan_id, step_index, agent, action, input_payload, meta_data=None):
        session = self.Session()
        sr = StepRecord(
            plan_id=plan_id,
            step_index=step_index,
            agent=agent,
            action=action,
            input_payload=json.dumps(input_payload),
            meta_data=json.dumps(meta_data or {}),
            status="pending"
        )
        session.add(sr)
        session.commit()
        step_id = sr.id
        session.close()
        return step_id

    def update_step_result(self, step_id, output_payload, status="success", meta_data=None):
        session = self.Session()
        sr = session.query(StepRecord).filter_by(id=step_id).first()
        if sr:
            sr.output_payload = json.dumps(output_payload)
            sr.status = status
            if meta_data:
                sr.meta_data = json.dumps(meta_data)
            session.commit()
        session.close()

    def get_steps_for_plan(self, plan_id):
        session = self.Session()
        rows = session.query(StepRecord).filter_by(plan_id=plan_id).order_by(StepRecord.step_index).all()
        out = []
        for r in rows:
            out.append({
                "id": r.id,
                "step_index": r.step_index,
                "agent": r.agent,
                "action": r.action,
                "input_payload": json.loads(r.input_payload) if r.input_payload else None,
                "output_payload": json.loads(r.output_payload) if r.output_payload else None,
                "status": r.status,
                "meta_data": json.loads(r.meta_data) if r.meta_data else {}
            })
        session.close()
        return out
