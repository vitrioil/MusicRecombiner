import uuid
from sqlalchemy.dialects.postgresql import UUID

import numpy as np

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

    command = db.relationship("Command", backref="storage", lazy="select", uselist=False)

    def __str__(self):
        return (f"Storage:[{self.storage_id}], Session:[{self.session_id}], "
                f"Music:[{self.music_id}]")


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
        return (f"Music:[{self.music_id}], sr:[{self.sample_rate}], "
                f"duration:[{self.duration}s], "
                f"channels:[{self.channels}] Stem:[{self.stem}]")


class Undo(db.Model):
    __tablename__ = "undo"

    undo_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    music_id = db.Column(UUID(as_uuid=True), db.ForeignKey("music.music_id"))

    total_augmentations = db.Column(db.Integer, nullable=False)
    current_augmentations = db.Column(db.Integer, nullable=False)
    stem_name = db.Column(db.String(20), nullable=False)

    def increment_augmentations(self):
        self.total_augmentations += 1
        self.current_augmentations = self.total_augmentations

    def shift_augmentation(self, delta=1):
        self.current_augmentations += delta
        self.current_augmentations = int(np.clip(self.current_augmentations, 0,
                                                 self.total_augmentations))

    def __str__(self):
        return (f"Undo: Music[{self.music_id}], Total Aug[{self.total_augmentations}], "
                f"Current Aug[{self.current_augmentations}], Stem[{self.stem_name}]")


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
        return (f"Volume:[{self.vol_id}], start:[{self.start}], end:[{self.end}], "
                f"volume:[{self.volume}] for {self.stem_name}")


class Copy(db.Model):
    __tablename__ = "copy"
    copy_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    copy_start = db.Column(db.Float)
    stem_name = db.Column(db.String(20))

    def __str__(self):
        return (f"Copy:[{self.copy_id}], start:[{self.start}], end:[{self.end}], "
                f"copy start:[{self.copy_start}] for {self.stem_name}")

class Overlay(db.Model):
    __tablename__ = "overlay"
    overlay_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    cmd_id = db.Column(UUID(as_uuid=True), db.ForeignKey("command.cmd_id"))
    start = db.Column(db.Float)
    end = db.Column(db.Float)
    overlay_start = db.Column(db.Float)
    stem_name = db.Column(db.String(20))

    def __str__(self):
        return (f"Overlay:[{self.overlay_id}], start:[{self.start}], end:[{self.end}], "
                f"overlay start:[{self.overlay_start}] for {self.stem_name}")

