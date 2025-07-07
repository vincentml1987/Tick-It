from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from . import db


# Association tables

deliverable_assets = db.Table(
    'deliverable_assets',
    db.Column('deliverable_id', db.Integer, db.ForeignKey('deliverable.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('asset.id'), primary_key=True)
)

deliverable_rooms = db.Table(
    'deliverable_rooms',
    db.Column('deliverable_id', db.Integer, db.ForeignKey('deliverable.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

deliverable_technicians = db.Table(
    'deliverable_technicians',
    db.Column('deliverable_id', db.Integer, db.ForeignKey('deliverable.id'), primary_key=True),
    db.Column('technician_id', db.Integer, db.ForeignKey('technician.id'), primary_key=True)
)

action_assets = db.Table(
    'action_assets',
    db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('asset.id'), primary_key=True)
)

action_rooms = db.Table(
    'action_rooms',
    db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

action_technicians = db.Table(
    'action_technicians',
    db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
    db.Column('technician_id', db.Integer, db.ForeignKey('technician.id'), primary_key=True)
)

action_files = db.Table(
    'action_files',
    db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True)
)

action_comments = db.Table(
    'action_comments',
    db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)

deliverable_files = db.Table(
    'deliverable_files',
    db.Column('deliverable_id', db.Integer, db.ForeignKey('deliverable.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True)
)

deliverable_comments = db.Table(
    'deliverable_comments',
    db.Column('deliverable_id', db.Integer, db.ForeignKey('deliverable.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)


class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='tech')

    deliverables = db.relationship('Deliverable', secondary=deliverable_technicians, back_populates='technicians')
    actions = db.relationship('Action', secondary=action_technicians, back_populates='technicians')


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(120))
    requester_email = db.Column(db.String(120))
    requester_phone = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    deliverables = db.relationship('Deliverable', back_populates='contact', cascade='all, delete-orphan')

    @property
    def code(self):
        return f"CON{self.id:07d}"


class Deliverable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))

    contact = db.relationship('Contact', back_populates='deliverables')
    actions = db.relationship('Action', back_populates='deliverable', cascade='all, delete-orphan')
    assets = db.relationship('Asset', secondary=deliverable_assets, back_populates='deliverables')
    rooms = db.relationship('Room', secondary=deliverable_rooms, back_populates='deliverables')
    technicians = db.relationship('Technician', secondary=deliverable_technicians, back_populates='deliverables')
    files = db.relationship('File', secondary=deliverable_files, back_populates='deliverables')
    comments = db.relationship('Comment', secondary=deliverable_comments, back_populates='deliverables')

    @property
    def code(self):
        return f"DEL{self.id:07d}"


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='To Do')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deliverable_id = db.Column(db.Integer, db.ForeignKey('deliverable.id'))

    deliverable = db.relationship('Deliverable', back_populates='actions')
    assets = db.relationship('Asset', secondary=action_assets, back_populates='actions')
    rooms = db.relationship('Room', secondary=action_rooms, back_populates='actions')
    technicians = db.relationship('Technician', secondary=action_technicians, back_populates='actions')
    files = db.relationship('File', secondary=action_files, back_populates='actions')
    comments = db.relationship('Comment', secondary=action_comments, back_populates='actions')

    @property
    def code(self):
        return f"ACT{self.id:07d}"


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    type = db.Column(db.String(120))
    model = db.Column(db.String(120))
    manufacturer = db.Column(db.String(120))
    serial_number = db.Column(db.String(120))
    purchase_date = db.Column(db.Date)
    warranty_info = db.Column(db.String(120))

    assigned_user_id = db.Column(db.Integer, db.ForeignKey('technician.id'))
    assigned_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    assigned_user = db.relationship('Technician', foreign_keys=[assigned_user_id])
    assigned_room = db.relationship('Room', foreign_keys=[assigned_room_id])

    deliverables = db.relationship('Deliverable', secondary=deliverable_assets, back_populates='assets')
    actions = db.relationship('Action', secondary=action_assets, back_populates='assets')


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(120))
    room_number = db.Column(db.String(120))
    description = db.Column(db.Text)

    assets = db.relationship('Asset', back_populates='assigned_room', cascade='all, delete')
    deliverables = db.relationship('Deliverable', secondary=deliverable_rooms, back_populates='rooms')
    actions = db.relationship('Action', secondary=action_rooms, back_populates='rooms')


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    path = db.Column(db.String(255))
    mime_type = db.Column(db.String(120))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('technician.id'))

    uploaded_by = db.relationship('Technician')
    deliverables = db.relationship('Deliverable', secondary=deliverable_files, back_populates='files')
    actions = db.relationship('Action', secondary=action_files, back_populates='files')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('technician.id'))

    user = db.relationship('Technician')
    deliverables = db.relationship('Deliverable', secondary=deliverable_comments, back_populates='comments')
    actions = db.relationship('Action', secondary=action_comments, back_populates='comments')
