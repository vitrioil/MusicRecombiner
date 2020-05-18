import uuid
from sqlalchemy.dialects.postgresql import UUID

#package import
from separator import db


class Session(db.Model):
    __tablename__ = "session"
    session_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    storage = db.relationship("Storage", backref="session", lazy="select")

    def __str__(self):
        return f"Session:[{self.session_id}]"


class Storage(db.Model):
    __tablename__ = "storage"
    storage_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey("session.session_id"))
    music_id = db.Column(UUID(as_uuid=True), db.ForeignKey("music.music_id"))

    command = db.relationship("Command", backref="storage", lazy="select")

    def __str__(self):
        return f"Storage:[{self.storage_id}], Session:[{self.session_id}], Music:[{self.music_id}]"


class Music(db.Model):
    __tablename__ = "music"
    music_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    file_path = db.Column(db.String(1000), nullable=False)
    sample_rate = db.Column(db.Integer, nullable=False, default=44_100)
    duration = db.Column(db.Integer, nullable=False)
    channels = db.Column(db.Integer, nullable=False, default=2)
    sample_width = db.Column(db.Integer, nullable=False)
    stem = db.Column(db.Integer, nullable=False)

    storage = db.relationship("Storage", backref="music", lazy="select", uselist=False)

    def __str__(self):
        return f"Music:[{self.music_id}], sr:[{self.sample_rate}], duration:[{self.duration}s], channels:[{self.channels}] Stem:[{self.stem}]"


class Command(db.Model):
    __tablename__ = "command"
    cmd_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    storage_id = db.Column(UUID(as_uuid=True), db.ForeignKey("storage.storage_id"))

    volume = db.relationship("Volume", uselist=True, backref="command")
    copy = db.relationship("Copy", uselist=True, backref="command")

    all_commands = {"Volume": volume, "Copy": copy}

    def __str__(self):
        return f"Command:[{self.cmd_id}], Storage:[{self.storage_id}]"


class Volume(db.Model):
    __tablename__ = "volume"
    vol_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    volume = db.Column(db.Float)
    stem_name = db.Column(db.String(20))

    def __str__(self):
        return f"Volume:[{self.vol_id}], start:[{self.start}], end:[{self.end}], volume:[{self.volume}] for {self.stem_name}"


class Copy(db.Model):
    __tablename__ = "copy"
    copy_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    copy_start = db.Column(db.Float)
    stem_name = db.Column(db.String(20))

    def __str__(self):
        return f"Copy:[{self.copy_id}], start:[{self.start}], end:[{self.end}], copy start:[{self.copy_start}] for {self.stem_name}"

