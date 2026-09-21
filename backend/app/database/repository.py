"""SQLAlchemy persistence; set DATABASE_URL to migrate the connection to PostgreSQL.

State is a versioned JSON snapshot; observations and datasets remain immutable.
"""
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Index, select, update
from sqlalchemy.orm import declarative_base, Session
from app.config import settings

Base = declarative_base()

class BridgeSnapshot(Base):
    __tablename__ = 'bridges'
    id = Column(String, primary_key=True)
    revision = Column(Integer, default=1, nullable=False)
    payload = Column(JSON, nullable=False)

class Record(Base):
    __tablename__ = 'records'
    id = Column(String, primary_key=True)
    kind = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    payload = Column(JSON, nullable=False)
    __table_args__ = (Index('idx_records_kind_created', 'kind', 'created_at'),)

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)
    bridge_id = Column(String, nullable=False)
    component_id = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    data_source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    __table_args__ = (Index('idx_observations_component_time','bridge_id','component_id','timestamp'),)

class Repository:
    def __init__(self, url=None):
        url = url or settings.database_url
        self.engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite') else {})
        Base.metadata.create_all(self.engine)

    def get_state(self):
        with Session(self.engine) as db:
            row = db.get(BridgeSnapshot, 'active')
            return (row.payload, row.revision) if row else (None, 0)

    def save_state(self, state, expected_revision):
        with Session(self.engine) as db, db.begin():
            row = db.get(BridgeSnapshot, 'active')
            if row is None:
                db.add(BridgeSnapshot(id='active', revision=1, payload=state))
                return 1
            result = db.execute(update(BridgeSnapshot).where(BridgeSnapshot.id=='active', BridgeSnapshot.revision==expected_revision).values(payload=state, revision=expected_revision+1))
            if result.rowcount != 1:
                raise RuntimeError('State changed in another session; refresh and retry.')
            return expected_revision+1

    def put(self, kind, identifier, payload):
        with Session(self.engine) as db, db.begin():
            db.merge(Record(id=identifier, kind=kind, payload=payload))

    def get(self, identifier):
        with Session(self.engine) as db:
            row = db.get(Record, identifier)
            return row.payload if row else None

    def list(self, kind, limit=100):
        with Session(self.engine) as db:
            return [r.payload for r in db.scalars(select(Record).where(Record.kind==kind).order_by(Record.created_at.desc()).limit(limit))]

    def add_observations(self, rows):
        with Session(self.engine) as db, db.begin():
            db.add_all([Observation(bridge_id=r['bridge_id'], component_id=r['component_id'], timestamp=r['timestamp'], data_source=r['data_source'], payload=r) for r in rows])
