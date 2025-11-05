from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import jwt, bcrypt, os
from datetime import datetime
import pytz

print("Flask server timezone:", datetime.now().astimezone().tzinfo)

# ==============================
# Config
# ==============================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}}, supports_credentials=True)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recruitment_system'
app.config['SECRET_KEY'] = 'jagoohire' 
mysql = MySQL(app)

# ==============================
# Helpers
# ==============================
def log_action(user_id, action, table_name):
    """Simpan audit log sederhana ke tabel audit_logs."""
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO audit_logs (user_id, action, table_name, timestamp) VALUES (%s,%s,%s,NOW())",
            (user_id, action, table_name)
        )
        mysql.connection.commit()
    finally:
        cur.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({'message': 'Token missing'}), 401
        token = token_header.replace("Bearer ", "")
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = {'user_id': data.get('user_id'), 'role': data.get('role')}
        except Exception as e:
            return jsonify({'message': 'Invalid token', 'error': str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(current_user, *args, **kwargs):
            if current_user.get('role') not in roles:
                return jsonify({'message': 'Access denied'}), 403
            return f(current_user, *args, **kwargs)
        return wrapper
    return decorator

# ==============================
# Auth
# ==============================
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'username and password required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password, role FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    stored_hash = user[1]
    if isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode('utf-8')
    else:
        stored_hash_bytes = stored_hash

    if bcrypt.checkpw(password.encode('utf-8'), stored_hash_bytes):
        token = jwt.encode({
            'user_id': user[0],
            'role': user[2],
            'exp': datetime.utcnow() + timedelta(hours=8)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'user_id': user[0], 'role': user[2]})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/register_initial', methods=['POST'])
def register_initial():
    """Buat initial admin (HCM) --- gunakan sekali."""
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'HCM')
    email = data.get('email')
    telp = data.get('telp')

    if not (username and password):
        return jsonify({'message': 'username and password required'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(username,password,role,email,telp,created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
                (username, hashed, role, email, telp))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Initial user created'})

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({'message': 'Logged out successfully'})

# ==============================
# Users (HCM)
# ==============================
@app.route('/users', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_user(current_user):
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # 'HCM','AM','Director'
    email = data.get('email')
    telp = data.get('telp')

    if not (username and password and role):
        return jsonify({'message': 'username, password, role required'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(username,password,role,email,telp,created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
                (username, hashed, role, email, telp))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'create user {username}', 'users')
    return jsonify({'message': 'User created'})

@app.route('/users', methods=['GET'])
@token_required
@role_required(['HCM'])
def get_users(current_user):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,username,email,telp,role,created_at FROM users")
    users = cur.fetchall()
    cur.close()
    return jsonify([{'id': u[0], 'username': u[1], 'email': u[2], 'telp': u[3], 'role': u[4], 'created_at': str(u[5])} for u in users])

@app.route('/users/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM'])
def update_user(current_user, id):
    data = request.json or {}
    username = data.get('username')
    role = data.get('role')
    email = data.get('email')
    telp = data.get('telp')
    password = data.get('password')

    cur = mysql.connection.cursor()
    if password:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("UPDATE users SET username=%s, role=%s, email=%s, telp=%s, password=%s WHERE id=%s",
                    (username, role, email, telp, hashed, id))
    else:
        cur.execute("UPDATE users SET username=%s, role=%s, email=%s, telp=%s WHERE id=%s",
                    (username, role, email, telp, id))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'update user id={id}', 'users')
    return jsonify({'message': 'User updated'})

@app.route('/users/<int:id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_user(current_user, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'delete user id={id}', 'users')
    return jsonify({'message': 'User deleted'})

# ==============================
# Candidates (HCM)
# ==============================
@app.route('/candidates', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_candidate(current_user):
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('no_telp')  
    domisili = data.get('domisili')
    applied_role = data.get('applied_role')
    status = data.get('status', 'Unconfirmed')  # default sesuai enum DB

    # Validasi input 
    if not (name and email and phone and domisili):
        return jsonify({'message': 'Name, email, phone, dan domisili wajib diisi'}), 400

    # Validasi status enum
    allowed_status = ['FCFS','Unconfirmed','Not Available','Onboarding','ASAP','Few Weeks','1 Month Notice','2 Month Notice']
    if status not in allowed_status:
        return jsonify({'message': f'Status tidak valid. Gunakan salah satu dari: {allowed_status}'}), 400

    cur = mysql.connection.cursor()

    # Cek duplikasi berdasarkan kombinasi email dan no_telp
    cur.execute("""
        SELECT id FROM candidates WHERE email=%s OR no_telp=%s
    """, (email, phone))
    duplicate = cur.fetchone()
    if duplicate:
        cur.close()
        return jsonify({'message': 'Kandidat dengan email atau nomor telepon tersebut sudah terdaftar'}), 400

    # Insert kandidat baru
    cur.execute("""
        INSERT INTO candidates (name, email, no_telp, domisili, applied_role, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (name, email, phone, domisili, applied_role, status))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'tambah kandidat {name}', 'candidates')
    return jsonify({'message': 'Kandidat berhasil ditambahkan'})


@app.route('/candidates', methods=['GET'])
@token_required
def get_candidates(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, no_telp, domisili, applied_role, status, created_at
        FROM candidates
        ORDER BY created_at DESC
    """)
    data = cur.fetchall()
    cur.close()

    candidates = [{
        'id': c[0],
        'name': c[1],
        'email': c[2],
        'phone': c[3],
        'domisili': c[4],
        'applied_role': c[5],
        'status': c[6],
        'created_at': str(c[7])
    } for c in data]

    return jsonify(candidates)


@app.route('/candidates/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM'])
def update_candidate(current_user, id):
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    domisili = data.get('domisili')
    applied_role = data.get('applied_role')
    status = data.get('status', 'Unconfirmed')

    allowed_status = ['FCFS','Unconfirmed','Not Available','Onboarding','ASAP','Few Weeks','1 Month Notice','2 Month Notice']
    if status not in allowed_status:
        return jsonify({'message': f'Status tidak valid. Pilihan: {allowed_status}'}), 400

    cur = mysql.connection.cursor()

    # Cek duplikasi pada kandidat lain
    cur.execute("""
        SELECT id FROM candidates
        WHERE (email=%s OR no_telp=%s) AND id != %s
    """, (email, phone, id))
    duplicate = cur.fetchone()
    if duplicate:
        cur.close()
        return jsonify({'message': 'Email atau nomor telepon sudah digunakan oleh kandidat lain'}), 400

    # Update kandidat
    cur.execute("""
        UPDATE candidates
        SET name=%s, email=%s, no_telp=%s, domisili=%s, applied_role=%s, status=%s
        WHERE id=%s
    """, (name, email, phone, domisili, applied_role, status, id))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'update kandidat id={id}', 'candidates')
    return jsonify({'message': 'Data kandidat berhasil diperbarui'})


@app.route('/candidates/<int:id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_candidate(current_user, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM candidates WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'hapus kandidat id={id}', 'candidates')
    return jsonify({'message': 'Kandidat berhasil dihapus'})

# ==============================
# Requests (HCM)
# ==============================

@app.route('/requests', methods=['GET'])
@token_required
def get_requests(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id, role, company_name, duration, quantity, max_salary, location,
            work_method, work_schedule, est_start_date, level, job_description,
            current_stage, created_at
        FROM requests
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()

    requests_data = [{
        'id': r[0],
        'role': r[1],
        'company_name': r[2],
        'duration': r[3],
        'quantity': r[4],
        'max_salary': float(r[5]) if r[5] is not None else None,
        'location': r[6],
        'work_method': r[7],
        'work_schedule': r[8],
        'est_start_date': str(r[9]) if r[9] else None,
        'level': r[10],
        'job_description': r[11],
        'current_stage': r[12],
        'created_at': str(r[13])
    } for r in rows]

    return jsonify(requests_data)


@app.route('/requests', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_request(current_user):
    data = request.json or {}

    role = data.get('role')
    company_name = data.get('company_name')
    duration = data.get('duration')
    quantity = data.get('quantity')
    max_salary = data.get('max_salary')
    location = data.get('location')
    work_method = data.get('work_method', 'onsite')
    work_schedule = data.get('work_schedule')
    est_start_date = data.get('est_start_date')
    level = data.get('level')
    job_description = data.get('job_description')
    current_stage = data.get('current_stage', 'New Request')

    # Validasi kolom wajib
    if not (role and company_name):
        return jsonify({'message': 'Kolom role dan company_name wajib diisi'}), 400

    # Validasi enum
    valid_work_methods = ['onsite', 'remote', 'hybrid']
    valid_stages = ['New Request', 'Aptitude', 'Technical', 'Professional', 'Trial', 'Onboarding', 'Finish']

    if work_method not in valid_work_methods:
        return jsonify({'message': f'Work method tidak valid. Pilihan: {valid_work_methods}'}), 400

    if current_stage not in valid_stages:
        return jsonify({'message': f'Stage tidak valid. Pilihan: {valid_stages}'}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO requests (
            role, company_name, duration, quantity, max_salary, location,
            work_method, work_schedule, est_start_date, level, job_description, current_stage
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        role, company_name, duration, quantity, max_salary, location,
        work_method, work_schedule, est_start_date, level, job_description, current_stage
    ))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'tambah request role={role}', 'requests')
    return jsonify({'message': 'Request berhasil ditambahkan'}), 201

@app.route('/requests/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM'])
def update_request(current_user, id):
    data = request.json or {}

    role = data.get('role')
    company_name = data.get('company_name')
    duration = data.get('duration')
    quantity = data.get('quantity')
    max_salary = data.get('max_salary')
    location = data.get('location')
    work_method = data.get('work_method')
    work_schedule = data.get('work_schedule')
    est_start_date = data.get('est_start_date')
    level = data.get('level')
    job_description = data.get('job_description')
    current_stage = data.get('current_stage')

    valid_work_methods = ['onsite', 'remote', 'hybrid']
    valid_stages = ['New Request', 'Aptitude', 'Technical', 'Professional', 'Trial', 'Onboarding', 'Finish']

    if work_method and work_method not in valid_work_methods:
        return jsonify({'message': f'Work method tidak valid. Pilihan: {valid_work_methods}'}), 400

    if current_stage and current_stage not in valid_stages:
        return jsonify({'message': f'Stage tidak valid. Pilihan: {valid_stages}'}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE requests
        SET role=%s, company_name=%s, duration=%s, quantity=%s, max_salary=%s,
            location=%s, work_method=%s, work_schedule=%s, est_start_date=%s,
            level=%s, job_description=%s, current_stage=%s
        WHERE id=%s
    """, (
        role, company_name, duration, quantity, max_salary, location,
        work_method, work_schedule, est_start_date, level, job_description,
        current_stage, id
    ))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'update request id={id}', 'requests')
    return jsonify({'message': 'Request berhasil diperbarui'})


@app.route('/requests/<int:id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_request(current_user, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM requests WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'hapus request id={id}', 'requests')
    return jsonify({'message': 'Request berhasil dihapus'})

# ==============================
# Request ↔ Candidate Mapping (HCM)
# ==============================
@app.route('/request_candidates', methods=['POST'])
@token_required
@role_required(['HCM'])
def link_request_candidate(current_user):
    data = request.json or {}
    request_id = data.get('request_id')
    candidate_id = data.get('candidate_id')

    if not request_id or not candidate_id:
        return jsonify({'error': 'request_id dan candidate_id wajib diisi'}), 400

    cur = mysql.connection.cursor()

    # Cek apakah kombinasi request-candidate sudah ada
    cur.execute("""
        SELECT id FROM request_candidates
        WHERE request_id = %s AND candidate_id = %s
    """, (request_id, candidate_id))
    existing = cur.fetchone()

    if existing:
        cur.close()
        return jsonify({'message': 'Kandidat sudah terhubung dengan request ini'}), 409

    # Tambahkan hubungan baru
    cur.execute("""
        INSERT INTO request_candidates (request_id, candidate_id, assigned_at)
        VALUES (%s, %s, NOW())
    """, (request_id, candidate_id))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'assign candidate_id={candidate_id} to request_id={request_id}', 'request_candidates')
    return jsonify({'message': 'Kandidat berhasil ditautkan ke request'}), 201

@app.route('/request_candidates', methods=['GET'])
@token_required
@role_required(['HCM'])
def get_all_request_candidates(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT rc.id, rc.request_id, c.id, c.name, c.email, c.no_telp, c.domisili, c.applied_role, c.status, rc.assigned_at
        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        ORDER BY rc.assigned_at DESC
    """)
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        result.append({
            'id': r[0],                # ID relasi request_candidate
            'request_id': r[1],        # ID request
            'candidate_id': r[2],      # ID kandidat
            'name': r[3],
            'email': r[4],
            'no_telp': r[5],
            'domisili': r[6],
            'applied_role': r[7],
            'status': r[8],
            'assigned_at': str(r[9]) if r[9] else None
        })

    return jsonify(result), 200


@app.route('/request_candidates/<int:request_id>', methods=['GET'])
@token_required
def get_request_candidates(current_user, request_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT rc.id, c.id, c.name, c.email, c.no_telp, c.domisili, c.applied_role, c.status, rc.assigned_at
        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        WHERE rc.request_id = %s
    """, (request_id,))
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'candidate_id': r[1],
            'name': r[2],
            'email': r[3],
            'no_telp': r[4],
            'domisili': r[5],
            'applied_role': r[6],
            'status': r[7],
            'assigned_at': str(r[8]) if r[8] else None
        })

    return jsonify(result)

# ==============================
# Update Request ↔ Candidate Mapping (HCM)
# ==============================
@app.route('/request_candidates/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM'])
def update_request_candidate(current_user, id):
    data = request.json or {}
    request_id = data.get('request_id')
    candidate_id = data.get('candidate_id')

    if not request_id or not candidate_id:
        return jsonify({'error': 'request_id dan candidate_id wajib diisi'}), 400

    cur = mysql.connection.cursor()

    # Cek apakah kombinasi request-candidate baru sudah ada
    cur.execute("""
        SELECT id FROM request_candidates
        WHERE request_id = %s AND candidate_id = %s AND id != %s
    """, (request_id, candidate_id, id))
    existing = cur.fetchone()
    if existing:
        cur.close()
        return jsonify({'message': 'Kandidat sudah terhubung dengan request ini'}), 409

    # Update relasi
    cur.execute("""
        UPDATE request_candidates
        SET request_id=%s, candidate_id=%s, assigned_at=NOW()
        WHERE id=%s
    """, (request_id, candidate_id, id))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'update request_candidate id={id} to request_id={request_id}, candidate_id={candidate_id}', 'request_candidates')
    return jsonify({'message': 'Relasi request-candidate berhasil diperbarui'}), 200

# ==============================
# Delete Request ↔ Candidate Mapping (HCM)
# ==============================
@app.route('/request_candidates/<int:id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_request_candidate(current_user, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM request_candidates WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'delete request_candidate id={id}', 'request_candidates')
    return jsonify({'message': 'Relasi request-candidate berhasil dihapus'}), 200

# ==============================
# Aptitude Tests (HCM)
# ==============================
@app.route('/aptitude_tests', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_aptitude_test(current_user):
    data = request.json or {}
    rc_id = data.get('request_candidate_id')
    test_date = data.get('test_date')
    must_have_skill = data.get('must_have_skill')
    motivation = data.get('motivation')  # enum('green_flag','red_flag')
    aptitude_score = data.get('aptitude_score')
    continue_next = data.get('continue_next')  # enum('ya','tidak')
    notes = data.get('notes')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO aptitude_tests (
            request_candidate_id, test_date, must_have_skill, motivation,
            aptitude_score, continue_next, notes, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (rc_id, test_date, must_have_skill, motivation, aptitude_score, continue_next, notes))
    mysql.connection.commit()

    if continue_next == 'ya':
        # Update status kandidat setelah aptitude test
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON c.id = rc.candidate_id
            SET c.status = 'ASAP'
            WHERE rc.id=%s
        """, (rc_id,))
        mysql.connection.commit()

    cur.close()
    log_action(current_user['user_id'], f'create aptitude_test for rc_id={rc_id}', 'aptitude_tests')
    return jsonify({'message': 'Aptitude test saved successfully'}), 201

@app.route('/aptitude_tests/<int:rc_id>', methods=['GET'])
@token_required
def get_aptitude_tests(current_user, rc_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, test_date, must_have_skill, motivation, aptitude_score, continue_next, notes, created_at
        FROM aptitude_tests
        WHERE request_candidate_id=%s
    """, (rc_id,))
    rows = cur.fetchall()
    cur.close()

    return jsonify([
        {
            'id': r[0],
            'test_date': str(r[1]) if r[1] else None,
            'must_have_skill': r[2],
            'motivation': r[3],
            'aptitude_score': float(r[4]) if r[4] is not None else None,
            'continue_next': r[5],
            'notes': r[6],
            'created_at': str(r[7])
        } for r in rows
    ])


# ==============================
# Technical Tests (AM)
# ==============================
@app.route('/technical_tests', methods=['POST'])
@token_required
@role_required(['AM'])
def add_technical_test(current_user):
    data = request.json or {}
    rc_id = data.get('request_candidate_id')
    test_date = data.get('test_date')
    aptitude_score = data.get('aptitude_score')
    domain12_score = data.get('domain12_score')
    stack_eval = data.get('stack_eval')
    portfolio_eval = data.get('portfolio_eval')
    continue_next = data.get('continue_next')
    notes = data.get('notes')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO technical_tests (
            request_candidate_id, test_date, aptitude_score, domain12_score,
            stack_eval, portfolio_eval, continue_next, notes, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (rc_id, test_date, aptitude_score, domain12_score, stack_eval, portfolio_eval, continue_next, notes))
    mysql.connection.commit()

    if continue_next == 'ya':
        # Update status kandidat setelah technical test
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON c.id = rc.candidate_id
            SET c.status = 'Few Weeks'
            WHERE rc.id=%s
        """, (rc_id,))
        mysql.connection.commit()

    cur.close()
    log_action(current_user['user_id'], f'create technical_test for rc_id={rc_id}', 'technical_tests')
    return jsonify({'message': 'Technical test saved successfully'}), 201


@app.route('/technical_tests/<int:rc_id>', methods=['GET'])
@token_required
def get_technical_tests(current_user, rc_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, test_date, aptitude_score, domain12_score, stack_eval,
               portfolio_eval, continue_next, notes, created_at
        FROM technical_tests
        WHERE request_candidate_id=%s
    """, (rc_id,))
    rows = cur.fetchall()
    cur.close()

    return jsonify([
        {
            'id': r[0],
            'test_date': str(r[1]) if r[1] else None,
            'aptitude_score': float(r[2]) if r[2] is not None else None,
            'domain12_score': float(r[3]) if r[3] is not None else None,
            'stack_eval': r[4],
            'portfolio_eval': r[5],
            'continue_next': r[6],
            'notes': r[7],
            'created_at': str(r[8])
        } for r in rows
    ])

@app.route('/technical_tests', methods=['GET'])
@token_required
@role_required(['AM', 'HCM', 'Director'])
def get_all_technical_tests(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id, request_candidate_id, test_date, aptitude_score, domain12_score,
            stack_eval, portfolio_eval, continue_next, notes, created_at
        FROM technical_tests
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()

    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'request_candidate_id': r[1],
            'test_date': str(r[2]) if r[2] else None,
            'aptitude_score': float(r[3]) if r[3] is not None else None,
            'domain12_score': float(r[4]) if r[4] is not None else None,
            'stack_eval': r[5],
            'portfolio_eval': r[6],
            'continue_next': r[7],
            'notes': r[8],
            'created_at': str(r[9])
        })

    return jsonify(result), 200

# ==============================
# Professional Tests (Director)
# ==============================
@app.route('/professional_tests', methods=['POST'])
@token_required
@role_required(['Director'])
def add_professional_test(current_user):
    data = request.json or {}
    rc_id = data.get('request_candidate_id')
    test_date = data.get('test_date')
    aptitude_score = data.get('aptitude_score')
    programming_fundamentals = data.get('programming_fundamentals')
    software_engineering = data.get('software_engineering')
    portfolio_eval = data.get('portfolio_eval')
    communication = data.get('communication')
    adaptability = data.get('adaptability')
    discipline = data.get('discipline')
    commitment = data.get('commitment')
    final_result = data.get('final_result')
    notes = data.get('notes')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO professional_tests (
            request_candidate_id, test_date, aptitude_score,
            programming_fundamentals, software_engineering, portfolio_eval,
            communication, adaptability, discipline, commitment,
            final_result, notes, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (
        rc_id, test_date, aptitude_score, programming_fundamentals,
        software_engineering, portfolio_eval, communication,
        adaptability, discipline, commitment, final_result, notes
    ))
    mysql.connection.commit()

    # Update status kandidat berdasarkan hasil akhir
    if final_result == 'lulus':
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON c.id = rc.candidate_id
            SET c.status = 'Onboarding'
            WHERE rc.id=%s
        """, (rc_id,))
    else:
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON c.id = rc.candidate_id
            SET c.status = 'Not Available'
            WHERE rc.id=%s
        """, (rc_id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'create professional_test for rc_id={rc_id}', 'professional_tests')
    return jsonify({'message': 'Professional test saved successfully'}), 201

@app.route('/professional_tests/<int:rc_id>', methods=['GET'])
@token_required
def get_professional_tests(current_user, rc_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, test_date, aptitude_score, programming_fundamentals,
               software_engineering, portfolio_eval, communication,
               adaptability, discipline, commitment, final_result,
               notes, created_at
        FROM professional_tests
        WHERE request_candidate_id=%s
    """, (rc_id,))
    rows = cur.fetchall()
    cur.close()

    return jsonify([
        {
            'id': r[0],
            'test_date': str(r[1]) if r[1] else None,
            'aptitude_score': float(r[2]) if r[2] is not None else None,
            'programming_fundamentals': r[3],
            'software_engineering': r[4],
            'portfolio_eval': r[5],
            'communication': r[6],
            'adaptability': r[7],
            'discipline': r[8],
            'commitment': r[9],
            'final_result': r[10],
            'notes': r[11],
            'created_at': str(r[12])
        } for r in rows
    ])

# ==============================
# Get all Professional Tests (Director)
# ==============================
@app.route('/professional_tests', methods=['GET'])
@token_required
def get_all_professional_tests(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, request_candidate_id, test_date, aptitude_score, programming_fundamentals,
               software_engineering, portfolio_eval, communication,
               adaptability, discipline, commitment, final_result,
               notes, created_at
        FROM professional_tests
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()

    return jsonify([
        {
            'id': r[0],
            'request_candidate_id': r[1],
            'test_date': str(r[2]) if r[2] else None,
            'aptitude_score': float(r[3]) if r[3] is not None else None,
            'programming_fundamentals': r[4],
            'software_engineering': r[5],
            'portfolio_eval': r[6],
            'communication': r[7],
            'adaptability': r[8],
            'discipline': r[9],
            'commitment': r[10],
            'final_result': r[11],
            'notes': r[12],
            'created_at': str(r[13])
        } for r in rows
    ])


# ==============================
# Feedbacks by Candidate
# ==============================
@app.route('/feedbacks/<int:candidate_id>', methods=['GET'])
@token_required
def get_feedbacks(current_user, candidate_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            f.id,
            u.username AS given_by,
            f.rating,
            f.comment,
            f.created_at
        FROM feedbacks f
        JOIN users u ON f.given_by = u.id
        WHERE f.candidate_id = %s
        ORDER BY f.created_at DESC
    """, (candidate_id,))
    rows = cur.fetchall()
    cur.close()

    feedbacks = [{
        'id': r[0],
        'given_by': r[1],
        'rating': float(r[2]) if r[2] is not None else None,
        'comment': r[3],
        'created_at': str(r[4])
    } for r in rows]

    return jsonify(feedbacks), 200


# ==============================
# Audit Logs (HCM only)
# ==============================
@app.route('/audit_logs', methods=['GET'])
@token_required
@role_required(['HCM'])
def get_audit_logs(current_user):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            al.id,
            u.username,
            al.action,
            al.table_name,
            al.timestamp
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
    """)
    logs = cur.fetchall()
    cur.close()

    result = [{
        'id': l[0],
        'username': l[1],
        'action': l[2],
        'table_name': l[3],
        'timestamp': str(l[4])
    } for l in logs]

    return jsonify(result), 200


@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    cur = mysql.connection.cursor()

    # ======================
    # Statistik Umum
    # ======================
    cur.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status")
    candidate_stats = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("SELECT COUNT(*) FROM requests")
    total_requests = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM feedbacks")
    total_feedbacks = cur.fetchone()[0] or 0

    # ======================
    # Active Requests
    # ======================
    cur.execute("""
        SELECT 
            r.id,
            r.role,
            r.quantity,
            r.company_name,
            r.max_salary
        FROM requests r
    """)
    requests_columns = [desc[0] for desc in cur.description]
    requests_data = [dict(zip(requests_columns, row)) for row in cur.fetchall()]

    # ======================
    # Fase Aptitude
    # ======================
    cur.execute("""
        SELECT 
            a.id AS aptitude_test_id,
            a.request_candidate_id,
            a.test_date,
            a.must_have_skill,
            a.motivation,
            a.aptitude_score,
            a.continue_next,
            a.notes,
            a.created_at AS test_created_at,
            rc.id AS rc_id,
            rc.request_id,
            rc.candidate_id,
            c.name AS candidate_name,
            c.email AS candidate_email,
            c.no_telp,
            c.domisili,
            c.applied_role,
            c.status AS candidate_status,
            r.role AS requested_role,
            r.company_name,
            r.location,
            r.work_method,
            r.work_schedule,
            r.level
        FROM aptitude_tests a
        JOIN request_candidates rc ON a.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        ORDER BY a.created_at DESC
    """)
    aptitude_columns = [desc[0] for desc in cur.description]
    aptitude_phase = [dict(zip(aptitude_columns, row)) for row in cur.fetchall()]

    # ======================
    # Fase Technical
    # ======================
    cur.execute("""
        SELECT
            t.id AS technical_test_id,
            t.request_candidate_id,
            t.test_date,
            t.aptitude_score,
            t.domain12_score,
            t.stack_eval,
            t.portfolio_eval,
            t.continue_next,
            t.notes,
            t.created_at AS test_created_at,
            rc.id AS rc_id,
            rc.request_id,
            rc.candidate_id,
            c.name AS candidate_name,
            c.email AS candidate_email,
            c.no_telp,
            c.domisili,
            c.applied_role,
            c.status AS candidate_status,
            r.role AS requested_role,
            r.company_name,
            r.location,
            r.work_method,
            r.work_schedule,
            r.level
        FROM technical_tests t
        JOIN request_candidates rc ON t.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        ORDER BY t.created_at DESC
    """)
    technical_columns = [desc[0] for desc in cur.description]
    technical_phase = [dict(zip(technical_columns, row)) for row in cur.fetchall()]

    # ======================
    # Fase Professional
    # ======================
    cur.execute("""
        SELECT
            p.id AS professional_test_id,
            p.request_candidate_id,
            p.test_date,
            p.aptitude_score,
            p.programming_fundamentals,
            p.software_engineering,
            p.portfolio_eval,
            p.communication,
            p.adaptability,
            p.discipline,
            p.commitment,
            p.final_result,
            p.notes,
            p.created_at AS test_created_at,
            rc.id AS rc_id,
            rc.request_id,
            rc.candidate_id,
            c.name AS candidate_name,
            c.email AS candidate_email,
            c.no_telp,
            c.domisili,
            c.applied_role,
            c.status AS candidate_status,
            r.role AS requested_role,
            r.company_name,
            r.location,
            r.work_method,
            r.work_schedule,
            r.level
        FROM professional_tests p
        JOIN request_candidates rc ON p.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        ORDER BY p.created_at DESC
    """)
    professional_columns = [desc[0] for desc in cur.description]
    professional_phase = [dict(zip(professional_columns, row)) for row in cur.fetchall()]

    for phase in [aptitude_phase, technical_phase, professional_phase]:
        for item in phase:
            if item.get("test_date"):
                dt = item["test_date"]
                if isinstance(dt, datetime):
                    item["test_date"] = dt.strftime("%d %b %Y %H:%M")
                else:
                    try:
                        parsed_dt = datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S")
                        item["test_date"] = parsed_dt.strftime("%d %b %Y %H:%M")
                    except:
                        pass

    # ======================
    # Today's Test Schedule
    # ======================
    cur.execute("""
        SELECT 'Aptitude' AS stage, a.test_date AS schedule_datetime, c.name AS candidate_name
        FROM aptitude_tests a
        JOIN request_candidates rc ON a.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        WHERE DATE(a.test_date) = CURDATE()

        UNION ALL

        SELECT 'Technical' AS stage, t.test_date AS schedule_datetime, c.name AS candidate_name
        FROM technical_tests t
        JOIN request_candidates rc ON t.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        WHERE DATE(t.test_date) = CURDATE()

        UNION ALL

        SELECT 'Professional' AS stage, p.test_date AS schedule_datetime, c.name AS candidate_name
        FROM professional_tests p
        JOIN request_candidates rc ON p.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        WHERE DATE(p.test_date) = CURDATE()
        ORDER BY schedule_datetime DESC
    """)
    todays_schedule_columns = [desc[0] for desc in cur.description]
    todays_schedule = [dict(zip(todays_schedule_columns, row)) for row in cur.fetchall()]

    for item in todays_schedule:
        if item.get("schedule_datetime"):
            dt = item["schedule_datetime"]
            if isinstance(dt, datetime):
                item["schedule_datetime"] = dt.strftime("%d %b %Y %H:%M")
            else:
                try:
                    parsed_dt = datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S")
                    item["schedule_datetime"] = parsed_dt.strftime("%d %b %Y %H:%M")
                except:
                    pass

    cur.close()

    return jsonify({
        'summary': {
            'total_requests': total_requests,
            'total_candidates': total_candidates,
            'total_feedbacks': total_feedbacks
        },
        'requests': requests_data,         
        'aptitude_phase': aptitude_phase,
        'technical_phase': technical_phase,
        'professional_phase': professional_phase,
        'todays_schedule': todays_schedule
    }), 200

# ==============================
# Run
# ==============================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
