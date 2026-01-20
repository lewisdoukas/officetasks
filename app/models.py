from __future__ import annotations

import enum
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Rank(enum.Enum):
    SXHS = "sxhs"
    ANXHS = "anxhs"
    TXHS = "txhs"
    LGOS = "lgos"
    YPLGOS = "yplgos"
    ANTHLGOS = "anthlgos"
    ANTHSTIS = "anthstis"
    ALXIAS = "alxias"
    EPXIAS = "epxias"
    LXIAS = "lxias"
    DNEAS = "dneas"
    MY = "my"


task_assignees = Table(
    "task_assignees",
    db.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(Enum(Rank), nullable=False)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    internal_phone = db.Column(db.String(20))
    mobile_phone = db.Column(db.String(20))

    active = db.Column(db.Boolean, default=True, nullable=False)

    # Admin auth fields (kept minimal)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # only needed for admins

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Flask-Login helpers
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def display_name(self) -> str:
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f"<User {self.id} {self.last_name} ({self.rank.value})>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    status = db.Column(db.String(20), default="active", nullable=False)  # active / archived

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    attachments = relationship("ProjectAttachment", back_populates="project", cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="tasks")

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    assign_date = db.Column(db.Date, default=date.today)
    deadline = db.Column(db.Date, nullable=True)
    delivery_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), default="backlog", nullable=False)  # backlog/in_progress/blocked/done
    priority = db.Column(db.String(10), default="medium", nullable=False) # low/medium/high

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    assignees = relationship("User", secondary=task_assignees, backref="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    def is_overdue(self) -> bool:
        return self.deadline is not None and self.delivery_date is None and self.deadline < date.today()


class TaskComment(db.Model):
    __tablename__ = "task_comments"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    task = relationship("Task", back_populates="comments")

    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    author = relationship("User")

    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)


class ProjectAttachment(db.Model):
    __tablename__ = "project_attachments"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="attachments")

    label = db.Column(db.String(120), nullable=False)
    path = db.Column(db.String(500), nullable=False)  # UNC path / file:/// / intranet URL

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
