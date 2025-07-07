from flask import Blueprint, request, jsonify, current_app, send_from_directory
from .models import db, Technician, Contact, Deliverable, Action, Asset, Room, File, Comment
from werkzeug.utils import secure_filename
import os

bp = Blueprint('api', __name__, url_prefix='/api')

# Helper to save uploaded file

def save_file(uploaded_file, uploaded_by):
    filename = secure_filename(uploaded_file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    uploaded_file.save(filepath)
    f = File(filename=filename, path=filepath, mime_type=uploaded_file.mimetype, uploaded_by=uploaded_by)
    db.session.add(f)
    return f

@bp.route('/contacts', methods=['GET'])
def list_contacts():
    contacts = Contact.query.all()
    result = []
    for c in contacts:
        result.append({'id': c.code, 'requester_name': c.requester_name, 'created_at': c.created_at.isoformat(), 'deliverable_count': len(c.deliverables)})
    return jsonify(result)

@bp.route('/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    c = Contact(
        requester_name=data.get('requester_name'),
        requester_email=data.get('requester_email'),
        requester_phone=data.get('requester_phone'),
        message=data.get('message')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'id': c.code, 'created_at': c.created_at.isoformat()}), 201

@bp.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    c = Contact.query.get_or_404(contact_id)
    deliverables = [{'id': d.code, 'title': d.title, 'status': d.status} for d in c.deliverables]
    return jsonify({'id': c.code, 'requester_name': c.requester_name, 'deliverables': deliverables})

@bp.route('/contacts/<int:contact_id>/deliverables', methods=['POST'])
def add_deliverable(contact_id):
    c = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    d = Deliverable(title=data.get('title'), description=data.get('description'), priority=data.get('priority'), status=data.get('status'))
    c.deliverables.append(d)
    db.session.add(d)
    db.session.commit()
    return jsonify({'id': d.code, 'title': d.title, 'status': d.status}), 201

@bp.route('/deliverables/<int:deliverable_id>', methods=['GET'])
def get_deliverable(deliverable_id):
    d = Deliverable.query.get_or_404(deliverable_id)
    actions = [{'id': a.code, 'description': a.description, 'status': a.status} for a in d.actions]
    return jsonify({'id': d.code, 'title': d.title, 'status': d.status, 'priority': d.priority, 'actions': actions})

@bp.route('/deliverables/<int:deliverable_id>', methods=['PATCH'])
def update_deliverable(deliverable_id):
    d = Deliverable.query.get_or_404(deliverable_id)
    data = request.get_json()
    if 'status' in data:
        d.status = data['status']
    if 'title' in data:
        d.title = data['title']
    db.session.commit()
    return jsonify({'id': d.code, 'status': d.status})

@bp.route('/deliverables/<int:deliverable_id>/actions', methods=['POST'])
def create_action(deliverable_id):
    d = Deliverable.query.get_or_404(deliverable_id)
    data = request.get_json()
    a = Action(description=data.get('description'), status=data.get('status'))
    d.actions.append(a)
    db.session.add(a)
    db.session.commit()
    return jsonify({'id': a.code, 'description': a.description, 'status': a.status}), 201

@bp.route('/actions/<int:action_id>', methods=['PATCH'])
def update_action(action_id):
    a = Action.query.get_or_404(action_id)
    data = request.get_json()
    if 'status' in data:
        a.status = data['status']
    if 'description' in data:
        a.description = data['description']
    if 'assigned_technician_id' in data:
        tech = Technician.query.get(data['assigned_technician_id'])
        if tech:
            if tech not in a.technicians:
                a.technicians.append(tech)
    db.session.commit()
    return jsonify({'id': a.code, 'status': a.status})

@bp.route('/assets', methods=['GET'])
def list_assets():
    assets = Asset.query.all()
    result = []
    for asset in assets:
        result.append({'id': asset.id, 'name': asset.name, 'type': asset.type, 'assigned_user_id': asset.assigned_user_id, 'assigned_room_id': asset.assigned_room_id})
    return jsonify(result)

@bp.route('/assets', methods=['POST'])
def create_asset():
    data = request.get_json()
    asset = Asset(
        name=data.get('name'),
        type=data.get('type'),
        model=data.get('model'),
        manufacturer=data.get('manufacturer'),
        serial_number=data.get('serial_number'),
        purchase_date=data.get('purchase_date'),
        warranty_info=data.get('warranty_info'),
        assigned_user_id=data.get('assigned_user_id'),
        assigned_room_id=data.get('assigned_room_id')
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify({'id': asset.id, 'name': asset.name}), 201

@bp.route('/assets/<int:asset_id>', methods=['PATCH'])
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json()
    for field in ['name', 'type', 'model', 'manufacturer', 'serial_number', 'warranty_info']:
        if field in data:
            setattr(asset, field, data[field])
    if 'assigned_user_id' in data:
        asset.assigned_user_id = data['assigned_user_id']
    if 'assigned_room_id' in data:
        asset.assigned_room_id = data['assigned_room_id']
    db.session.commit()
    return jsonify({'id': asset.id})

@bp.route('/rooms', methods=['GET'])
def list_rooms():
    rooms = Room.query.all()
    return jsonify([{'id': r.id, 'building': r.building, 'room_number': r.room_number} for r in rooms])

@bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    room = Room(building=data.get('building'), room_number=data.get('room_number'), description=data.get('description'))
    db.session.add(room)
    db.session.commit()
    return jsonify({'id': room.id}), 201

@bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    comment = Comment(content=data['content'], user_id=data.get('user_id'))
    parent_type = data.get('parent_type')
    parent_id = data.get('parent_id')
    if parent_type == 'Deliverable':
        deliverable = Deliverable.query.get_or_404(parent_id)
        deliverable.comments.append(comment)
    elif parent_type == 'Action':
        action = Action.query.get_or_404(parent_id)
        action.comments.append(comment)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'id': comment.id}), 201

@bp.route('/files', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    parent_type = request.form.get('parent_type')
    parent_id = request.form.get('parent_id')
    uploaded_by_id = request.form.get('uploaded_by_id')
    tech = Technician.query.get(uploaded_by_id) if uploaded_by_id else None
    f = save_file(uploaded_file, tech)
    if parent_type == 'Deliverable':
        deliverable = Deliverable.query.get_or_404(parent_id)
        deliverable.files.append(f)
    elif parent_type == 'Action':
        action = Action.query.get_or_404(parent_id)
        action.files.append(f)
    db.session.commit()
    return jsonify({'id': f.id, 'filename': f.filename})

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
