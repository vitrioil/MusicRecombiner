import uuid
from sqlalchemy.dialects.postgresql import UUID

#package import
from separator import db


class Session(db.Model):
    __tablename__ = "session"
    session_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    music_id = db.Column(UUID(as_uuid=True), db.ForeignKey("music.music_id"))

    storage = db.relationship("Storage", backref="session", lazy="dynamic")


class Storage(db.Model):
    __tablename__ = "storage"
    storage_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey("session.session_id"))
    command = db.relationship("Command", backref="storage", lazy="dynamic")


class Music(db.Model):
    __tablename__ = "music"
    music_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    file_path = db.Column(db.String(50), nullable=False)
    sample_rate = db.Column(db.Integer, nullable=False, default=44_100)
    duration = db.Column(db.Integer, nullable=False)
    channels = db.Column(db.Integer, nullable=False, default=2)
    sample_width = db.Column(db.Integer, nullable=False)

    storage = db.relationship("Storage", backref="music", lazy="dynamic")


class Command(db.Model):
    __tablename__ = "command"
    cmd_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    storage_id = db.Column(UUID(as_uuid=True), db.ForeignKey("storage.storage_id"))

    volume = db.relationship("Volume", uselist=False, backref="command")
    copy = db.relationship("Copy", uselist=False, backref="command")


class Volume(db.Model):
    __tablename__ = "volume"
    vol_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    volume = db.Column(db.Float)


class Copy(db.Model):
    __tablename__ = "copy"
    copy_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    copy_start = db.Column(db.Float)

