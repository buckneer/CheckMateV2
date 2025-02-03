from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from datetime import date  # Add this line for 'date'

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models

# Professor
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', backref='students')


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', backref='subjects')


class StudentSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    student = db.relationship('Student', backref='student_subjects')
    subject = db.relationship('Subject', backref='student_subjects')
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='unique_student_subject'),)


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)

    professor = db.relationship('Professor', backref='classes')
    subject = db.relationship('Subject', backref='classes')


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='present')  # e.g., 'present', 'absent'

    class_ = db.relationship('Class', backref='attendances')
    student = db.relationship('Student', backref='attendances')

    __table_args__ = (db.UniqueConstraint('class_id', 'student_id', name='unique_attendance'),)


# Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Professor.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_professor = Professor(name=data['name'], email=data['email'], password=hashed_password)
    try:
        db.session.add(new_professor)
        db.session.commit()
        return jsonify({'message': 'Professor registered successfully!'}), 201
    except:
        return jsonify({'message': 'Registration failed. Email might be already in use.'}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    professor = Professor.query.filter_by(email=data['email']).first()
    if not professor or not check_password_hash(professor.password, data['password']):
        return jsonify({'message': 'Login failed. Check email and password.'}), 401
    token = jwt.encode({'id': professor.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                       app.config['SECRET_KEY'])
    return jsonify({'token': token})


@app.route('/subjects', methods=['GET'])
@token_required
def get_subjects(current_user):
    subjects = Subject.query.filter_by(professor_id=current_user.id).all()

    if not subjects:
        return jsonify({'message': 'No subjects found.', 'subjects': []}), 200

    subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]

    return jsonify({'message': 'Subjects fetched successfully!', 'subjects': subject_list}), 200


@app.route('/subjects', methods=['POST'])
@token_required
def add_subject(current_user):
    data = request.get_json()
    subject_name = data.get('name')

    if not subject_name:
        return jsonify({'message': 'Subject name is required.'}), 400

    # Check for duplicate subject for the professor
    if Subject.query.filter_by(name=subject_name, professor_id=current_user.id).first():
        return jsonify({'message': 'Subject already exists.'}), 400

    new_subject = Subject(name=subject_name, professor_id=current_user.id)

    try:
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'message': 'Subject created successfully!',
                        'subject': {'id': new_subject.id, 'name': new_subject.name}}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to create subject.', 'error': str(e)}), 500


@app.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    # Fetch students for the logged-in professor
    students = Student.query.filter_by(professor_id=current_user.id).all()

    if not students:
        return jsonify({'message': 'No students found.', 'students': []}), 200

    student_list = [
        {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email
        } for student in students
    ]

    return jsonify({
        'message': 'Students fetched successfully!',
        'students': student_list
    }), 200


@app.route('/students', methods=['POST'])
@token_required
def add_student(current_user):
    data = request.get_json()

    # Validate input data
    if not data.get('email') or not data.get('first_name') or not data.get('last_name'):
        return jsonify({'message': 'Missing required fields.'}), 400

    # Check for existing student with the same email
    if Student.query.filter_by(email=data['email'], professor_id=current_user.id).first():
        return jsonify({'message': 'Student already exists under your account.'}), 400

    new_student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        professor_id=current_user.id
    )

    try:
        db.session.add(new_student)
        db.session.commit()
        return jsonify({
            'message': 'Student added successfully!',
            'student': {
                'id': new_student.id,
                'first_name': new_student.first_name,
                'last_name': new_student.last_name,
                'email': new_student.email
            }
        }), 201
    except Exception as e:
        return jsonify({'message': 'Failed to add student.', 'error': str(e)}), 500


@app.route('/assign_student', methods=['POST'])
def assign_student():
    data = request.get_json()

    student_id = data.get('student_id')
    subject_id = data.get('subject_id')

    if not student_id or not subject_id:
        return jsonify({"message": "Student ID and Subject ID are required."}), 400

    existing_relation = StudentSubject.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if existing_relation:
        return jsonify({"message": "Student is already assigned to this subject."}), 400

    new_assignment = StudentSubject(student_id=student_id, subject_id=subject_id)
    try:
        db.session.add(new_assignment)
        db.session.commit()
        return jsonify({"message": "Student successfully assigned to subject."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to assign student to subject: {str(e)}"}), 500



@app.route("/subject/<int:subject_id>/students", methods=["GET"])
def get_subject_students(subject_id):
    # Fetch the subject to ensure it exists
    subject = Subject.query.get(subject_id)
    if not subject:
        return {"error": "Subject not found"}, 404

    # Fetch students associated with the subject
    student_subjects = StudentSubject.query.filter_by(subject_id=subject_id).all()

    # Build the response
    students = [
        {
            "id": ss.student.id,
            "first_name": ss.student.first_name,
            "last_name": ss.student.last_name
        }
        for ss in student_subjects
    ]

    return {"id": subject.id, "name": subject.name, "students": students}, 200


@app.route('/classes', methods=['POST'])
@token_required
def create_class(current_user):
    """
    Create a new class for a specific subject.
    """
    data = request.get_json()
    subject_id = data.get('subject_id')

    # Validate input
    if not subject_id:
        return jsonify({"message": "Subject ID is required."}), 400

    # Check if the subject exists and belongs to the current professor
    subject = Subject.query.filter_by(id=subject_id, professor_id=current_user.id).first()
    if not subject:
        return jsonify({"message": "Subject not found or does not belong to the current professor."}), 404

    # Create a new class
    new_class = Class(professor_id=current_user.id, subject_id=subject_id)
    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify({
            "message": "Class created successfully!",
            "class": {
                "id": new_class.id,
                "subject_id": new_class.subject_id,
                "subject_name": subject.name,
                "professor_id": new_class.professor_id,
                "date": new_class.date
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to create class: {str(e)}"}), 500


@app.route('/classes/<int:class_id>/attendance', methods=['POST'])
@token_required
def mark_attendance(current_user, class_id):
    """
    Mark attendance for a student in a specific class.
    """
    data = request.get_json()
    student_id = data.get('student_id')
    status = data.get('status', 'present').lower()  # Default to 'present'

    # Validate input
    if not student_id:
        return jsonify({"message": "Student ID is required."}), 400

    # Check if the class exists and belongs to the current professor
    class_ = Class.query.filter_by(id=class_id, professor_id=current_user.id).first()
    if not class_:
        return jsonify({"message": "Class not found or does not belong to the current professor."}), 404

    # Check if the student is associated with the subject of the class
    student_subject = StudentSubject.query.filter_by(student_id=student_id, subject_id=class_.subject_id).first()
    if not student_subject:
        return jsonify({"message": "Student is not assigned to this subject."}), 400

    # Check if attendance already exists for this student in this class
    existing_attendance = Attendance.query.filter_by(class_id=class_id, student_id=student_id).first()
    if existing_attendance:
        return jsonify({"message": "Attendance already marked for this student in this class."}), 400

    # Mark attendance
    new_attendance = Attendance(class_id=class_id, student_id=student_id, status=status)
    try:
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({"message": "Attendance marked successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to mark attendance: {str(e)}"}), 500


@app.route('/classes/<int:class_id>', methods=['GET'])
@token_required
def get_class_attendance(current_user, class_id):
    """
    Get details of a class and its attendance.
    """
    # Check if the class exists and belongs to the current professor
    class_ = Class.query.filter_by(id=class_id, professor_id=current_user.id).first()
    if not class_:
        return jsonify({"message": "Class not found or does not belong to the current professor."}), 404

    # Get all students in the subject of the class
    students = StudentSubject.query.filter_by(subject_id=class_.subject_id).all()

    # Build attendance data
    attendance_data = []
    for ss in students:
        attendance = Attendance.query.filter_by(class_id=class_id, student_id=ss.student_id).first()
        attendance_data.append({
            "student_id": ss.student.id,
            "first_name": ss.student.first_name,
            "last_name": ss.student.last_name,
            "status": attendance.status if attendance else "absent"
        })

    return jsonify({
        "class": {
            "id": class_.id,
            "subject_id": class_.subject_id,
            "subject_name": class_.subject.name,
            "professor_id": class_.professor_id,
            "date": class_.date
        },
        "attendance": attendance_data
    }), 200


@app.route('/subject/<int:subject_id>/classes', methods=['GET'])
@token_required
def get_classes_for_subject(current_user, subject_id):
    # First, ensure the subject belongs to the logged-in professor.
    subject = Subject.query.filter_by(id=subject_id, professor_id=current_user.id).first()
    if not subject:
        return jsonify({"message": "Subject not found or access denied"}), 404

    # Get all classes for this subject
    classes = Class.query.filter_by(subject_id=subject_id, professor_id=current_user.id).all()
    classes_list = [{"id": cls.id, "date": cls.date.isoformat()} for cls in classes]
    return jsonify({"classes": classes_list}), 200


# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
