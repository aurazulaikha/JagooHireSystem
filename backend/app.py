from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import jwt, bcrypt, os
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
def log_action(user_id, action, table_name, record_id=None, old_values=None, new_values=None):
    try:
        cur = mysql.connection.cursor()
        
        # Build detailed action description
        action_description = action
        if record_id:
            action_description += f" record_id={record_id}"
        if old_values and new_values:
            action_description += f" - changed: {old_values} -> {new_values}"
        
        cur.execute("""
            INSERT INTO audit_logs (user_id, action, table_name, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, action_description, table_name))
        
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error logging action: {e}")
        return False

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
# Users Management (HCM only)
# ==============================
@app.route('/users', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_user(current_user):
    data = request.json or {}
    
    required_fields = ['username', 'password', 'role']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'Username, password, dan role wajib diisi'}), 400

    username = data['username']
    password = data['password']
    role = data['role']
    email = data.get('email', '')
    telp = data.get('telp', '')

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (username, password, role, email, telp, created_at) 
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (username, hashed_password, role, email, telp))
        
    user_id = cur.lastrowid
    mysql.connection.commit()
    cur.close()
        
    log_action(current_user['user_id'], f'Tambah user : {username}, user id : {user_id}', 'manage users')
    return jsonify({'message': 'User berhasil dibuat'}), 201

@app.route('/users', methods=['GET'])
@token_required
@role_required(['HCM'])
def get_users(current_user):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,username,email,telp,role,created_at FROM users")
    users = cur.fetchall()
    cur.close()
    
    result = []
    for user in users:
        result.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'telp': user[3],
            'role': user[4],
            'created_at': str(user[5])
        })
        
    return jsonify(result), 200

@app.route('/users/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM'])
def update_user(current_user, id):
    data = request.json or {}
    
    required_fields = ['username', 'role']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'Username dan role wajib diisi'}), 400

    username = data['username']
    role = data['role']
    email = data.get('email', '')
    telp = data.get('telp', '')
    password = data.get('password')

    cur = mysql.connection.cursor()
    
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("""
            UPDATE users SET username=%s, role=%s, email=%s, telp=%s, password=%s 
            WHERE id=%s
        """, (username, role, email, telp, hashed_password, id))
    else:
        cur.execute("""
            UPDATE users SET username=%s, role=%s, email=%s, telp=%s 
            WHERE id=%s
        """, (username, role, email, telp, id))
        
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Edit user, user id : {id}', 'manage users')
    return jsonify({'message': 'User berhasil diperbarui'}), 200

@app.route('/users/<int:id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_user(current_user, id):
    cur = mysql.connection.cursor()
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE id=%s", (id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({'message': 'User tidak ditemukan'}), 404

    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Hapus user, user id : {id}', 'manage users')
    return jsonify({'message': 'User berhasil dihapus'}), 200

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

    log_action(current_user['user_id'], f'Assign kandidate id : {candidate_id} to request id : {request_id}', 'request candidates')
    return jsonify({'message': 'Kandidat berhasil ditautkan ke request'}), 201

# ==============================
# Lihat semua Request ↔ Candidate (HCM & AM & Director)
# ==============================
@app.route('/request_candidates', methods=['GET'])
@token_required
@role_required(['HCM', 'AM', 'Director'])
def get_all_request_candidates(current_user):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            rc.id AS request_candidate_id,
            r.id AS request_id,
            c.name AS nama_kandidat,
            c.applied_role AS role_dilamar,
            r.role AS role_dibutuhkan,
            c.email AS email_kandidat,
            c.no_telp,
            c.domisili,
            r.company_name AS perusahaan,
            r.location AS lokasi_kerja,
            r.work_method AS metode_kerja,
            r.work_schedule AS jadwal_kerja,
            r.level AS level,
            r.duration AS durasi,
            r.quantity AS kuantitas,
            r.max_salary AS maks_gaji,
            r.current_stage AS stage,
            c.status AS status_kandidat,
            rc.assigned_at

        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id

        ORDER BY rc.assigned_at DESC
    """)

    rows = cur.fetchall()
    cur.close()

    result = []
    for i, r in enumerate(rows, start=1):
        result.append({
            "no": i,
            "request_candidate_id": r[0],
            "request_id": r[1],
            "nama_kandidat": r[2],
            "role_dilamar": r[3],
            "role_dibutuhkan": r[4],
            "email_kandidat": r[5],
            "no_telp": r[6],
            "domisili": r[7],
            "perusahaan": r[8],
            "lokasi_kerja": r[9],
            "metode_kerja": r[10],
            "jadwal_kerja": r[11],
            "level": r[12],
            "durasi": r[13],
            "kuantitas": r[14],
            "maks_gaji": float(r[15]) if r[15] else None,
            "stage": r[16],
            "status_kandidat": r[17],
            "assigned_at": str(r[18]) if r[18] else None
        })

    return jsonify(result), 200

# ==============================
# GET BY ID
# ==============================
@app.route('/request_candidates/<int:id>', methods=['GET'])
@token_required
@role_required(['HCM', 'AM', 'Director'])
def get_request_candidate_by_id(current_user, id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            rc.id,
            r.id AS request_id,
            c.id AS candidate_id,
            c.name,
            r.role,
            c.applied_role,
            r.current_stage,
            c.status
        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        WHERE rc.id = %s
    """, (id,))

    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({'error': 'Data tidak ditemukan'}), 404

    return jsonify({
        "request_candidate_id": row[0],
        "request_id": row[1],
        "candidate_id": row[2],
        "nama_kandidat": row[3],
        "role_dibutuhkan": row[4],
        "role_dilamar": row[5],
        "stage": row[6],
        "status_kandidat": row[7]
    }), 200

# ==============================
# UPDATE
# ==============================
@app.route('/request_candidates/<int:id>', methods=['PUT'])
@token_required
@role_required(['HCM', 'AM', 'Director'])
def update_request_candidate(current_user, id):
    data = request.get_json()

    request_id = data.get('request_id')
    candidate_id = data.get('candidate_id')

    if not request_id or not candidate_id:
        return jsonify({'message': 'Semua field wajib diisi'}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE request_candidates
        SET request_id = %s, candidate_id = %s
        WHERE id = %s
    """, (request_id, candidate_id, id))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Edit request kandidat, id : {id}', 'requests candidates')
    return jsonify({'message': 'Berhasil diperbarui'}), 200

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

    log_action(current_user['user_id'], f'Hapus request kandidat, id : {id}', 'request candidates')
    return jsonify({'message': 'Relasi request-candidate berhasil dihapus'}), 200

# =========================================
# Aptitude Tests - Combined View (HCM only)
# =========================================
@app.route('/aptitude_tests/overview', methods=['GET'])
@token_required
@role_required(['HCM'])
def get_aptitude_overview(current_user):
    cur = mysql.connection.cursor()

    # Kandidat yang BELUM melakukan aptitude test
    cur.execute("""
        SELECT 
            a.id AS aptitude_test_id,
            rc.id AS rc_id,
            a.test_date,
            a.aptitude_score,
            a.motivation,
            a.must_have_skill,
            a.continue_next,
            a.notes,
            a.created_at AS test_created_at,
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
        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        LEFT JOIN aptitude_tests a ON a.request_candidate_id = rc.id
        WHERE a.aptitude_score IS NULL
        ORDER BY rc.id DESC
    """)
    pending_aptitude = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]

    # Kandidat yang SUDAH melakukan aptitude test
    cur.execute("""
        SELECT 
            a.id AS aptitude_test_id,
            rc.id AS rc_id,
            a.test_date,
            a.aptitude_score,
            a.motivation,
            a.must_have_skill,
            a.continue_next,
            a.notes,
            a.created_at AS test_created_at,
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
        WHERE 
            a.test_date IS NOT NULL
            AND a.aptitude_score IS NOT NULL
            AND a.motivation IS NOT NULL
            AND a.must_have_skill IS NOT NULL
        ORDER BY a.created_at DESC
    """)
    done_aptitude = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]

    cur.close()

    return jsonify({
        'pending_aptitude': pending_aptitude,
        'done_aptitude': done_aptitude
    }), 200

# ==============================
# Atur Jadwal Aptitude Test
# ==============================
@app.route('/aptitude_tests/schedule', methods=['PATCH'])
@token_required
@role_required(['HCM'])
def set_aptitude_schedule(current_user):
    data = request.json or {}
    rc_id = data.get('request_candidate_id')
    test_date = data.get('test_date')

    if not rc_id or not test_date:
        return jsonify({'message': 'request_candidate_id dan test_date wajib'}), 400

    cur = mysql.connection.cursor()

    # Cek apakah data sudah ada
    cur.execute("SELECT id FROM aptitude_tests WHERE request_candidate_id=%s", (rc_id,))
    
    if cur.fetchone():
        cur.execute("UPDATE aptitude_tests SET test_date=%s WHERE request_candidate_id=%s", 
                   (test_date, rc_id))
    else:
        cur.execute("INSERT INTO aptitude_tests (request_candidate_id, test_date, created_at) VALUES (%s, %s, NOW())", 
                   (rc_id, test_date))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Atur jadwal, request kandidat id: {rc_id}', 'aptitude tests')
    return jsonify({'message': 'Tanggal tes berhasil diatur'}), 200

# ==============================
# Create/Update Aptitude Tests (HCM)
# ==============================
@app.route('/aptitude_tests', methods=['POST'])
@token_required
@role_required(['HCM'])
def add_aptitude_test(current_user):
    data = request.json
    rc_id = data.get('request_candidate_id')
    
    required_fields = ['test_date', 'aptitude_score', 'motivation', 'must_have_skill', 'continue_next']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'Semua field wajib diisi'}), 400

    cur = mysql.connection.cursor()

    # Cek apakah data sudah ada
    cur.execute("SELECT id FROM aptitude_tests WHERE request_candidate_id=%s", (rc_id,))

    if cur.fetchone():
        # Update existing record
        cur.execute("""
            UPDATE aptitude_tests SET
                test_date=%s, aptitude_score=%s, motivation=%s,
                must_have_skill=%s, continue_next=%s, notes=%s, created_at=NOW()
            WHERE request_candidate_id=%s
        """, (data['test_date'], data['aptitude_score'], data['motivation'],
              data['must_have_skill'], data['continue_next'], data.get('notes'), rc_id))
    else:
        # Insert new record
        cur.execute("""
            INSERT INTO aptitude_tests (
                request_candidate_id, test_date, aptitude_score, motivation,
                must_have_skill, continue_next, notes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (rc_id, data['test_date'], data['aptitude_score'], data['motivation'],
              data['must_have_skill'], data['continue_next'], data.get('notes')))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Penilaian, request kandidat id : {rc_id}', 'aptitude tests')
    return jsonify({'message': 'Aptitude test saved successfully'}), 201

# ==============================
# Get Aptitude Test by RC ID
# ==============================
@app.route('/aptitude_tests/<int:rc_id>', methods=['GET'])
@token_required
def get_aptitude_tests(current_user, rc_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, test_date, must_have_skill, motivation, aptitude_score, continue_next, notes, created_at
        FROM aptitude_tests
        WHERE request_candidate_id=%s
    """, (rc_id,))

    results = []
    for row in cur.fetchall():
        results.append({
            'id': row[0],
            'test_date': str(row[1]) if row[1] else None,
            'must_have_skill': row[2],
            'motivation': row[3],
            'aptitude_score': float(row[4]) if row[4] else None,
            'continue_next': row[5],
            'notes': row[6],
            'created_at': str(row[7])
        })
    
    cur.close()
    return jsonify(results)

# ==============================
# Delete Aptitude
# ==============================
@app.route('/aptitude_tests/<int:test_id>', methods=['DELETE'])
@token_required
@role_required(['HCM'])
def delete_aptitude_test(current_user, test_id):
    cur = mysql.connection.cursor()

    # Cek apakah data sudah ada
    cur.execute("SELECT id, request_candidate_id FROM aptitude_tests WHERE id=%s", (test_id,))
    test_data = cur.fetchone()
    
    if not test_data:
        cur.close()
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    request_candidate_id = test_data[1]

    cur.execute("DELETE FROM aptitude_tests WHERE id=%s", (test_id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Hapus data penilaian, request kandidat id : {request_candidate_id}', 'aptitude tests')
    return jsonify({'message': 'Aptitude test berhasil dihapus'}), 200

# ==============================
# Technical Tests - Combined View
# ==============================
@app.route('/technical_tests/overview', methods=['GET'])
@token_required
@role_required(['AM'])
def get_technical_overview(current_user):
    cur = mysql.connection.cursor()

    # Kandidat yang BELUM melakukan technical test
    cur.execute("""
        SELECT 
            a.id AS aptitude_test_id,
            a.request_candidate_id,
            t.test_date,
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
        LEFT JOIN technical_tests t ON t.request_candidate_id = a.request_candidate_id
        WHERE 
            t.domain12_score IS NULL 
            AND a.continue_next = 'ya'
        ORDER BY a.created_at DESC
    """)
    pending_technical = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]

    # Kandidat yang SUDAH melakukan technical test
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
        WHERE 
            t.test_date IS NOT NULL
            AND t.domain12_score IS NOT NULL
            AND t.stack_eval IS NOT NULL
            AND t.portfolio_eval IS NOT NULL
        ORDER BY t.created_at DESC
    """)
    done_technical = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]

    cur.close()

    return jsonify({
        'pending_technical': pending_technical,
        'done_technical': done_technical
    }), 200

# ==============================
# Atur Jadwal Technical Test
# ==============================
@app.route('/technical_tests/schedule', methods=['PATCH'])
@token_required
@role_required(['AM'])
def set_technical_schedule(current_user):
    data = request.json or {}
    rc_id = data.get('rc_id')
    test_date = data.get('test_date')

    if not rc_id or not test_date:
        return jsonify({'message': 'rc_id dan test_date wajib diisi'}), 400

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM technical_tests WHERE request_candidate_id=%s", (rc_id,))

    if cur.fetchone():
        cur.execute("UPDATE technical_tests SET test_date=%s WHERE request_candidate_id=%s", 
                   (test_date, rc_id))
    else:
        cur.execute("INSERT INTO technical_tests (request_candidate_id, test_date, created_at) VALUES (%s, %s, NOW())", 
                   (rc_id, test_date))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Atur jadwal, request kandidat id: {rc_id}', 'technical tests')
    return jsonify({'message': 'Tanggal tes berhasil diatur'}), 200


# ==============================
# Create/Update Technical Tests (AM)
# ==============================
@app.route('/technical_tests', methods=['POST'])
@token_required
@role_required(['AM'])
def add_technical_test(current_user):
    data = request.json or {}
    rc_id = data.get('rc_id')
    
    required_fields = ['test_date', 'domain12_score', 'stack_eval', 'portfolio_eval', 'continue_next']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'Semua field wajib diisi'}), 400

    cur = mysql.connection.cursor()

    # Ambil aptitude_score dari aptitude_tests
    cur.execute("""
        SELECT aptitude_score
        FROM aptitude_tests
        WHERE request_candidate_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (rc_id,))
    aptitude_row = cur.fetchone()
    aptitude_score = aptitude_row[0] if aptitude_row else None

    # CEK APAKAH SUDAH ADA DATA TECHNICAL TEST
    cur.execute("SELECT id FROM technical_tests WHERE request_candidate_id = %s", (rc_id,))

    if cur.fetchone():
        # UPDATE JIKA SUDAH ADA
        cur.execute("""
            UPDATE technical_tests SET
                test_date=%s, aptitude_score=%s, domain12_score=%s,
                stack_eval=%s, portfolio_eval=%s, continue_next=%s, notes=%s, created_at=NOW()
            WHERE request_candidate_id=%s
        """, (data['test_date'], aptitude_score, data['domain12_score'],
              data['stack_eval'], data['portfolio_eval'], data['continue_next'], 
              data.get('notes'), rc_id))
    else:
        # INSERT BARU JIKA BELUM ADA
        cur.execute("""
            INSERT INTO technical_tests (
                request_candidate_id, test_date, aptitude_score, domain12_score,
                stack_eval, portfolio_eval, continue_next, notes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (rc_id, data['test_date'], aptitude_score, data['domain12_score'],
              data['stack_eval'], data['portfolio_eval'], data['continue_next'], 
              data.get('notes')))

    mysql.connection.commit()

        # Update status kandidat setelah technical test
    if data['continue_next'] == 'ya':
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON c.id = rc.candidate_id
            SET c.status = 'Few Weeks'
            WHERE rc.id=%s
        """, (rc_id,))
        mysql.connection.commit()

    cur.close()
    
    log_action(current_user['user_id'], f'Penilaian, request kandidat id : {rc_id}', 'technical tests')
    return jsonify({'message': 'Technical test saved successfully'}), 201

# ==============================
# Get Technical Test by RC ID
# ==============================
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
    
    results = []
    for row in cur.fetchall():
        results.append({
            'id': row[0],
            'test_date': str(row[1]) if row[1] else None,
            'aptitude_score': float(row[2]) if row[2] is not None else None,
            'domain12_score': float(row[3]) if row[3] is not None else None,
            'stack_eval': row[4],
            'portfolio_eval': row[5],
            'continue_next': row[6],
            'notes': row[7],
            'created_at': str(row[8])
        })
    
    cur.close()
    return jsonify(results)

# ==============================
# Delete Technical Test
# ==============================
@app.route('/technical_tests/<int:test_id>', methods=['DELETE'])
@token_required
@role_required(['AM'])
def delete_technical_test(current_user, test_id):
    cur = mysql.connection.cursor()

    # cek apakah data ada
    cur.execute("SELECT id FROM technical_tests WHERE id=%s", (test_id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    # hapus data
    cur.execute("DELETE FROM technical_tests WHERE id=%s", (test_id,))
    mysql.connection.commit()
    cur.close()

    # log aktivitas
    log_action(current_user['user_id'], f'Hapus data penilaian, id : {test_id}', 'technical tests')

    return jsonify({'message': 'Technical test berhasil dihapus'}), 200

# ==============================
# Professional Tests - Combined View (FIXED)
# ==============================
@app.route('/professional_tests/overview', methods=['GET'])
@token_required
@role_required(['Director'])
def get_professional_overview(current_user):
    cur = mysql.connection.cursor()

    # Kandidat yang BELUM menjalani professional test (FIXED QUERY)
    cur.execute("""
        SELECT 
            rc.id AS request_candidate_id,
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
            r.level,
            a.aptitude_score,
            t.domain12_score AS technical_score,
            t.continue_next,
            p.test_date,
            p.programming_fundamentals,
            p.id AS professional_test_id  -- tambahkan ini untuk edit/hapus
        FROM request_candidates rc
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        JOIN aptitude_tests a ON a.request_candidate_id = rc.id
        JOIN technical_tests t ON t.request_candidate_id = rc.id
        LEFT JOIN professional_tests p ON p.request_candidate_id = rc.id
        WHERE p.programming_fundamentals IS NULL -- Belum professional test atau belum complete  
            AND t.continue_next = 'ya'
        ORDER BY rc.id DESC
    """)
    pending_columns = [d[0] for d in cur.description]
    pending_list = [dict(zip(pending_columns, row)) for row in cur.fetchall()]

    # Kandidat yang SUDAH menjalani professional test (done)
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
            r.level,
            t.domain12_score AS technical_score
        FROM professional_tests p
        JOIN request_candidates rc ON p.request_candidate_id = rc.id
        JOIN candidates c ON rc.candidate_id = c.id
        JOIN requests r ON rc.request_id = r.id
        LEFT JOIN technical_tests t ON t.request_candidate_id = rc.id
        WHERE p.final_result IS NOT NULL
                AND p.programming_fundamentals IS NOT NULL
                AND p.software_engineering IS NOT NULL
                AND p.portfolio_eval IS NOT NULL
                AND p.communication IS NOT NULL
                AND p.adaptability IS NOT NULL
                AND p.discipline IS NOT NULL
                AND p.commitment IS NOT NULL

        ORDER BY p.created_at DESC
    """)
    done_columns = [d[0] for d in cur.description]
    done_list = [dict(zip(done_columns, row)) for row in cur.fetchall()]

    cur.close()

    return jsonify({
        "pending_professional": pending_list,
        "done_professional": done_list
    }), 200

# ==============================
# Schedule Professional Test
# ==============================
@app.route('/professional_tests/schedule', methods=['PATCH'])
@token_required
@role_required(['Director'])
def schedule_professional_test(current_user):
    data = request.json or {}
    rc_id = data.get('request_candidate_id')
    test_date = data.get('test_date')

    if not rc_id or not test_date:
        return jsonify({"message": "request_candidate_id and test_date required"}), 400

    cur = mysql.connection.cursor()

    # Buat record minimal jika belum ada, atau update test_date jika sudah ada
    cur.execute("SELECT id FROM professional_tests WHERE request_candidate_id=%s", (rc_id,))
    exists = cur.fetchone()

    if exists:
        cur.execute("""
            UPDATE professional_tests
            SET test_date = %s
            WHERE request_candidate_id = %s
        """, (test_date, rc_id))
    else:
        cur.execute("""
            INSERT INTO professional_tests (request_candidate_id, test_date, created_at)
            VALUES (%s, %s, NOW())
        """, (rc_id, test_date))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Atur jadwal, request kandidat id : {rc_id}', 'professional tests')

    return jsonify({"message": "Schedule saved successfully"}), 200

# ==============================
# Insert / Update Professional Test
# ==============================
@app.route('/professional_tests', methods=['POST'])
@token_required
@role_required(['Director'])
def add_professional_test(current_user):
    data = request.json or {}

    rc_id = data.get('request_candidate_id')
    if not rc_id:
        return jsonify({"message": "request_candidate_id required"}), 400

    cur = mysql.connection.cursor()

    # Ambil aptitude_score dari aptitude_tests (ambil yang terbaru jika ada)
    cur.execute("""
        SELECT aptitude_score
        FROM aptitude_tests
        WHERE request_candidate_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (rc_id,))
    aptitude_row = cur.fetchone()
    aptitude_score = aptitude_row[0] if aptitude_row else None

    # Extract values (frontend tidak perlu mengirim aptitude_score)
    test_date = data.get('test_date')
    programming_fundamentals = data.get('programming_fundamentals')
    software_engineering = data.get('software_engineering')
    portfolio_eval = data.get('portfolio_eval')
    communication = data.get('communication')
    adaptability = data.get('adaptability')
    discipline = data.get('discipline')
    commitment = data.get('commitment')
    final_result = data.get('final_result')
    notes = data.get('notes')

    # Validation enum
    valid_eval = ['incompetent', 'developing', 'advance']
    valid_result = ['lulus', 'tidak_lulus']

    for key, val in {
        'software_engineering': software_engineering,
        'portfolio_eval': portfolio_eval,
        'communication': communication,
        'adaptability': adaptability,
        'discipline': discipline,
        'commitment': commitment
    }.items():
        if val and val not in valid_eval:
            cur.close()
            return jsonify({"message": f"{key} invalid. Must be one of {valid_eval}"}), 400

    if final_result and final_result not in valid_result:
        cur.close()
        return jsonify({"message": f"final_result invalid. Must be one of {valid_result}"}), 400

    # programming_fundamentals should be numeric (decimal)
    if programming_fundamentals is not None:
        try:
            programming_fundamentals = float(programming_fundamentals)
        except (ValueError, TypeError):
            cur.close()
            return jsonify({"message": "programming_fundamentals must be a number"}), 400

    # Check existing record professional_tests
    cur.execute("SELECT id FROM professional_tests WHERE request_candidate_id=%s", (rc_id,))
    exists = cur.fetchone()

    if exists:
        # UPDATE existing
        cur.execute("""
            UPDATE professional_tests
            SET test_date=%s,
                aptitude_score=%s,
                programming_fundamentals=%s,
                software_engineering=%s,
                portfolio_eval=%s,
                communication=%s,
                adaptability=%s,
                discipline=%s,
                commitment=%s,
                final_result=%s,
                notes=%s,
                created_at=NOW()
            WHERE request_candidate_id=%s
        """, (
            test_date,
            aptitude_score,
            programming_fundamentals,
            software_engineering,
            portfolio_eval,
            communication,
            adaptability,
            discipline,
            commitment,
            final_result,
            notes,
            rc_id
        ))
    else:
        # INSERT baru
        cur.execute("""
            INSERT INTO professional_tests (
                request_candidate_id, test_date, aptitude_score,
                programming_fundamentals, software_engineering, portfolio_eval,
                communication, adaptability, discipline, commitment,
                final_result, notes, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """, (
            rc_id,
            test_date,
            aptitude_score,
            programming_fundamentals,
            software_engineering,
            portfolio_eval,
            communication,
            adaptability,
            discipline,
            commitment,
            final_result,
            notes
        ))

    mysql.connection.commit()

    # UPDATE candidate + request stage
    if final_result == "lulus":
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON rc.candidate_id = c.id
            SET c.status = 'Onboarding'
            WHERE rc.id = %s
        """, (rc_id,))

        cur.execute("""
            UPDATE requests r
            JOIN request_candidates rc ON rc.request_id = r.id
            SET r.current_stage = 'Finish'
            WHERE rc.id = %s
        """, (rc_id,))
    else:
        cur.execute("""
            UPDATE candidates c
            JOIN request_candidates rc ON rc.candidate_id = c.id
            SET c.status = 'Not Available'
            WHERE rc.id = %s
        """, (rc_id,))

        cur.execute("""
            UPDATE requests r
            JOIN request_candidates rc ON rc.request_id = r.id
            SET r.current_stage = 'Professional'
            WHERE rc.id = %s
        """, (rc_id,))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Penilaian, request kandidat id : {rc_id}', 'professional tests')

    return jsonify({"message": "Professional test saved successfully"}), 201

# ==============================
# GET ONE TEST BY request_candidate_id
# ==============================
@app.route('/professional_tests/<int:rc_id>', methods=['GET'])
@token_required
def get_professional_test_detail(current_user, rc_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, test_date, aptitude_score, programming_fundamentals,
               software_engineering, portfolio_eval, communication,
               adaptability, discipline, commitment, final_result,
               notes, created_at
        FROM professional_tests
        WHERE request_candidate_id = %s
        LIMIT 1
    """, (rc_id,))

    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({})

    return jsonify({
        'id': row[0],
        'test_date': str(row[1]) if row[1] else None,
        'aptitude_score': float(row[2]) if row[2] is not None else None,
        'programming_fundamentals': float(row[3]) if row[3] is not None else None,
        'software_engineering': row[4],
        'portfolio_eval': row[5],
        'communication': row[6],
        'adaptability': row[7],
        'discipline': row[8],
        'commitment': row[9],
        'final_result': row[10],
        'notes': row[11],
        'created_at': str(row[12]) if row[12] else None
    })

# ==============================
# DELETE Professional Test
# ==============================
@app.route('/professional_tests/<int:test_id>', methods=['DELETE'])
@token_required
@role_required(['Director'])
def delete_professional_test(current_user, test_id):
    cur = mysql.connection.cursor()
    
    # Get request_candidate_id before deleting for logging
    cur.execute("SELECT request_candidate_id FROM professional_tests WHERE id=%s", (test_id,))
    result = cur.fetchone()
    
    if not result:
        cur.close()
        return jsonify({"message": "Professional test not found"}), 404
    
    request_candidate_id = result[0]
    
    # Delete the professional test
    cur.execute("DELETE FROM professional_tests WHERE id=%s", (test_id,))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], f'Hapus data penilaian, id : {request_candidate_id}', 'professional tests')

    return jsonify({"message": "Professional test deleted successfully"}), 200

# ==============================
# FEEDBACK - GET ALL CANDIDATES
# ==============================
@app.route('/candidates/for-feedback', methods=['GET'])
@token_required
def get_candidates_for_feedback(current_user):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        cur = mysql.connection.cursor()

        # Ambil SEMUA candidate dengan field baru
        cur.execute("""
            SELECT 
                c.id AS candidate_id,
                c.name,
                c.email,
                c.no_telp,
                c.domisili,
                c.status,
                c.created_at,
                CASE 
                    WHEN f.id IS NOT NULL THEN TRUE 
                    ELSE FALSE 
                END AS already_feedback
            FROM candidates c
            LEFT JOIN feedbacks f ON c.id = f.candidate_id
            ORDER BY c.created_at DESC
        """)

        rows = cur.fetchall()
        cur.close()

        data = []
        for r in rows:
            data.append({
                "candidate_id": r[0],
                "name": r[1],
                "email": r[2],
                "telepon": r[3],  # dari no_telp
                "domisili": r[4],
                "status": r[5],
                "created_at": r[6].isoformat() if r[6] else None,
                "already_feedback": bool(r[7])
            })

        return jsonify({
            "success": True,
            "total": len(data),
            "data": data
        }), 200

    except Exception as e:
        print(f"Error in get_candidates_for_feedback: {str(e)}")
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    
# ============================================
# CREATE FEEDBACK
# ============================================
@app.route('/feedbacks', methods=['POST'])
@token_required
def create_feedback(current_user):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        data = request.get_json()
        candidate_id = data.get('candidate_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not candidate_id or rating is None:
            return jsonify({'message': 'candidate_id dan rating wajib diisi'}), 400

        try:
            rating_value = float(rating)
            if rating_value < 0 or rating_value > 5:
                return jsonify({'message': 'Rating harus 0.00 - 5.00'}), 400
        except:
            return jsonify({'message': 'Rating harus angka'}), 400

        cur = mysql.connection.cursor()

        # Cek kandidat exists
        cur.execute("SELECT id FROM candidates WHERE id = %s", (candidate_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Kandidat tidak ditemukan'}), 404

        # Insert feedback
        cur.execute("""
            INSERT INTO feedbacks (candidate_id, given_by, rating, comment, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (candidate_id, current_user['user_id'], rating_value, comment))

        mysql.connection.commit()
        new_id = cur.lastrowid
        cur.close()

        log_action(current_user['user_id'], f'Feedback, kandidat id : {candidate_id}', 'feedbacks')

        return jsonify({
            "success": True,
            "message": "Feedback berhasil ditambahkan",
            "feedback_id": new_id
        }), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

# ============================================
# GET ALL FEEDBACKS
# ============================================
@app.route('/feedbacks', methods=['GET'])
@token_required
def get_all_feedbacks(current_user):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT 
                f.id,
                f.rating,
                f.comment,
                f.created_at,
                c.id AS candidate_id,
                c.name AS candidate_name,
                c.email AS candidate_email,
                c.no_telp AS candidate_telepon,
                c.domisili AS candidate_domisili,
                c.status AS candidate_status,
                u.username AS given_by_name
            FROM feedbacks f
            JOIN candidates c ON f.candidate_id = c.id
            JOIN users u ON f.given_by = u.id
            ORDER BY f.created_at DESC
        """)

        rows = cur.fetchall()
        cur.close()

        data = []
        for r in rows:
            data.append({
                "id": r[0],
                "rating": float(r[1]) if r[1] is not None else None,
                "comment": r[2],
                "created_at": r[3].isoformat() if r[3] else None,
                "candidate_id": r[4],
                "candidate_name": r[5],
                "candidate_email": r[6],
                "candidate_telepon": r[7],
                "candidate_domisili": r[8],
                "candidate_status": r[9],
                "given_by": r[10]
            })

        return jsonify({
            "success": True,
            "total": len(data),
            "data": data
        }), 200

    except Exception as e:
        print(f"Error in get_all_feedbacks: {str(e)}")
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    
# ============================================
# GET DETAIL FEEDBACK BY ID
# ============================================
# ============================================
# GET DETAIL FEEDBACK BY ID
# ============================================
@app.route('/feedbacks/<int:feedback_id>', methods=['GET'])
@token_required
def get_feedback(current_user, feedback_id):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT 
                f.id, 
                f.rating, 
                f.comment, 
                f.created_at,
                c.id AS candidate_id, 
                c.name AS candidate_name, 
                c.email AS candidate_email,
                c.no_telp AS candidate_telepon,
                c.domisili AS candidate_domisili,
                c.status AS candidate_status,
                u.username AS given_by_name, 
                u.role AS given_by_role
            FROM feedbacks f
            JOIN candidates c ON f.candidate_id = c.id
            JOIN users u ON f.given_by = u.id
            WHERE f.id = %s
        """, (feedback_id,))

        r = cur.fetchone()
        cur.close()

        if not r:
            return jsonify({'message': 'Feedback tidak ditemukan'}), 404

        feedback = {
            "id": r[0],
            "rating": float(r[1]) if r[1] is not None else None,
            "comment": r[2],
            "created_at": r[3].isoformat() if r[3] else None,
            "candidate": {
                "id": r[4],
                "name": r[5],
                "email": r[6],
                "telepon": r[7],
                "domisili": r[8],
                "status": r[9]
            },
            "given_by": {
                "name": r[10],
                "role": r[11]
            }
        }

        return jsonify({"success": True, "data": feedback}), 200

    except Exception as e:
        print(f"Error in get_feedback: {str(e)}")
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    
# ============================================
# UPDATE FEEDBACK BY ID
# ============================================
@app.route('/feedbacks/<int:feedback_id>', methods=['PUT'])
@token_required
def update_feedback(current_user, feedback_id):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')

        if rating is None:
            return jsonify({'message': 'Rating wajib diisi'}), 400

        try:
            rating_value = float(rating)
            if rating_value < 0 or rating_value > 5:
                return jsonify({'message': 'Rating harus 0.00 - 5.00'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Rating harus angka'}), 400

        cur = mysql.connection.cursor()

        try:
            # Cek apakah feedback exists
            cur.execute("SELECT id, candidate_id FROM feedbacks WHERE id = %s", (feedback_id,))
            feedback_data = cur.fetchone()
            
            if not feedback_data:
                return jsonify({'message': 'Feedback tidak ditemukan'}), 404

            candidate_id = feedback_data[1]

            # Update feedback
            cur.execute("""
                UPDATE feedbacks 
                SET rating = %s, comment = %s
                WHERE id = %s
            """, (rating_value, comment, feedback_id))

            mysql.connection.commit()

            log_action(current_user['user_id'], f'Edit feedback, kandidat id : {candidate_id}', 'feedbacks')
            return jsonify({
                "success": True,
                "message": "Feedback berhasil diupdate",
                "feedback_id": feedback_id
            }), 200

        except Exception as e:
            mysql.connection.rollback()
            raise e

    except Exception as e:
        print(f"Error in update_feedback: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

    finally:
        if 'cur' in locals():
            cur.close()

# ============================================
# DELETE FEEDBACK BY ID
# ============================================
@app.route('/feedbacks/<int:feedback_id>', methods=['DELETE'])
@token_required
def delete_feedback(current_user, feedback_id):
    try:
        if current_user.get('role') != 'Director':
            return jsonify({'message': 'Akses ditolak'}), 403

        cur = mysql.connection.cursor()

        try:
            # Cek apakah feedback exists
            cur.execute("SELECT id, candidate_id FROM feedbacks WHERE id = %s", (feedback_id,))
            feedback_data = cur.fetchone()
            
            if not feedback_data:
                return jsonify({'message': 'Feedback tidak ditemukan'}), 404

            candidate_id = feedback_data[1]

            # Delete feedback
            cur.execute("DELETE FROM feedbacks WHERE id = %s", (feedback_id,))

            mysql.connection.commit()

            log_action(current_user['user_id'], f'Hapus feedback, kandidat id : {candidate_id}', 'feedbacks')
            return jsonify({
                "success": True,
                "message": "Feedback berhasil dihapus"
            }), 200

        except Exception as e:
            mysql.connection.rollback()
            raise e

    except Exception as e:
        print(f"Error in delete_feedback: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500

    finally:
        if 'cur' in locals():
            cur.close()


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


# ==============================
# Dashboard
# ==============================
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
# Profile Management
# ==============================
@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get profile user yang sedang login"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, username, email, telp, role, created_at 
        FROM users WHERE id=%s
    """, (current_user['user_id'],))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user[0],
        'username': user[1],
        'email': user[2],
        'telp': user[3],
        'role': user[4],
        'created_at': str(user[5])
    })

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update profile user yang sedang login"""
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    telp = data.get('telp')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    cur = mysql.connection.cursor()
    
    if new_password:
        if not current_password:
            return jsonify({'message': 'Current password required to change password'}), 400
        
        cur.execute("SELECT password FROM users WHERE id=%s", (current_user['user_id'],))
        user = cur.fetchone()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        stored_hash = user[0]
        if isinstance(stored_hash, str):
            stored_hash_bytes = stored_hash.encode('utf-8')
        else:
            stored_hash_bytes = stored_hash

        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash_bytes):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("""
            UPDATE users 
            SET username=%s, email=%s, telp=%s, password=%s 
            WHERE id=%s
        """, (username, email, telp, hashed_new_password, current_user['user_id']))
    else:
        cur.execute("""
            UPDATE users 
            SET username=%s, email=%s, telp=%s 
            WHERE id=%s
        """, (username, email, telp, current_user['user_id']))

    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], 'Edit profil', 'profil')
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/profile/password', methods=['PUT'])
@token_required
def change_password(current_user):
    """Ganti password khusus"""
    data = request.json or {}
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': 'Current password and new password are required'}), 400

    cur = mysql.connection.cursor()
    
    cur.execute("SELECT password FROM users WHERE id=%s", (current_user['user_id'],))
    user = cur.fetchone()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    stored_hash = user[0]
    if isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode('utf-8')
    else:
        stored_hash_bytes = stored_hash

    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash_bytes):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_new_password, current_user['user_id']))
    mysql.connection.commit()
    cur.close()

    log_action(current_user['user_id'], 'Ganti password', 'users')
    return jsonify({'message': 'Password changed successfully'})

# ==============================
# Run
# ==============================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
