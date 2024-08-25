from flask import Blueprint, request, jsonify
from app import db
from models import User, Task
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)
task_bp = Blueprint('task', __name__)


# User Registration
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


# User Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity={'username': user.username})
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


# Create a new task
@task_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    data = request.get_json()

    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'Todo'),
        priority=data.get('priority', 'Low'),
        due_date=data.get('due_date'),
        owner=user
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201


# Read tasks
@task_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    tasks = Task.query.filter_by(user_id=user.id).all()

    task_list = [{'id': task.id, 'title': task.title, 'description': task.description,
                  'status': task.status, 'priority': task.priority, 'due_date': str(task.due_date)} for task in tasks]

    return jsonify(task_list), 200


# Update a task
@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.due_date = data.get('due_date', task.due_date)
    db.session.commit()

    return jsonify({'message': 'Task updated successfully'}), 200


# Delete a task
@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200


# Filter and Search Tasks
@task_bp.route('/tasks/search', methods=['GET'])
@jwt_required()
def search_tasks():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    status = request.args.get('status')
    priority = request.args.get('priority')
    search_query = request.args.get('q')

    query = Task.query.filter_by(user_id=user.id)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if search_query:
        query = query.filter((Task.title.contains(search_query)) | (Task.description.contains(search_query)))

    tasks = query.all()
    task_list = [{'id': task.id, 'title': task.title, 'description': task.description,
                  'status': task.status, 'priority': task.priority, 'due_date': str(task.due_date)} for task in tasks]

    return jsonify(task_list), 200
