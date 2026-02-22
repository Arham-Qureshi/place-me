from flask_cloudflared import run_with_cloudflared
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from functools import wraps
from db_config import get_db

app = Flask(__name__)
app.secret_key = 'placement_secret_key_2024'




# ── Helper: login required decorator ────────────────────────
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('index'))
            if role and session.get('role') != role:
                flash('Unauthorized access.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'company':
            return redirect(url_for('company_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    email_or_user = request.form.get('email')
    password = request.form.get('password')

    db = get_db()
    if not db:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('index'))
    cur = db.cursor(dictionary=True)

    if role == 'student':
        cur.execute("SELECT * FROM Students WHERE email=%s AND password=%s",
                    (email_or_user, password))
        user = cur.fetchone()
        if user:
            session['user_id'] = user['student_id']
            session['role'] = 'student'
            session['name'] = user['first_name']
            cur.close(); db.close()
            return redirect(url_for('student_dashboard'))

    elif role == 'company':
        cur.execute("SELECT * FROM Companies WHERE email=%s AND password=%s",
                     (email_or_user, password))
        user = cur.fetchone()
        if user:
            session['user_id'] = user['company_id']
            session['role'] = 'company'
            session['name'] = user['name']
            cur.close(); db.close()
            return redirect(url_for('company_dashboard'))

    elif role == 'admin':
        cur.execute("SELECT * FROM Administrator WHERE username=%s AND password=%s",
                     (email_or_user, password))
        user = cur.fetchone()
        if user:
            session['user_id'] = user['admin_id']
            session['role'] = 'admin'
            session['name'] = 'Admin'
            cur.close(); db.close()
            return redirect(url_for('admin_dashboard'))

    cur.close(); db.close()
    flash('Invalid credentials. Please try again.', 'danger')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        db = get_db()
        if not db:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('register'))
        cur = db.cursor()

        try:
            if role == 'student':
                cur.execute(
                    """INSERT INTO Students
                       (roll_number, first_name, last_name, email, password, branch, cgpa)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (request.form['roll_number'],
                     request.form['first_name'],
                     request.form.get('last_name', ''),
                     request.form['email'],
                     request.form['password'],
                     request.form['branch'],
                     request.form.get('cgpa', 0))
                )
            elif role == 'company':
                cur.execute(
                    """INSERT INTO Companies
                       (name, email, password, website, location)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (request.form['name'],
                     request.form['email'],
                     request.form['password'],
                     request.form.get('website', ''),
                     request.form.get('location', ''))
                )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Registration failed: {e}', 'danger')
        finally:
            cur.close(); db.close()

        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ══════════════════════════════════════════════════════════════
#  STUDENT ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    sid = session['user_id']
    # Count applications
    cur.execute("SELECT COUNT(*) AS cnt FROM Applications WHERE student_id=%s", (sid,))
    app_count = cur.fetchone()['cnt']
    # Count selected
    cur.execute("SELECT COUNT(*) AS cnt FROM Applications WHERE student_id=%s AND status='Selected'", (sid,))
    sel_count = cur.fetchone()['cnt']
    # Recent jobs
    cur.execute("""SELECT j.job_id, c.name AS company_name, j.job_role, j.package,
                          j.eligibility_cgpa, j.deadline
                   FROM Jobs j JOIN Companies c ON j.company_id=c.company_id
                   WHERE j.status='Active' AND j.deadline>=CURDATE()
                   ORDER BY j.created_at DESC LIMIT 5""")
    recent_jobs = cur.fetchall()
    cur.close(); db.close()
    return render_template('student_dashboard.html',
                           app_count=app_count, sel_count=sel_count,
                           recent_jobs=recent_jobs)


@app.route('/student/jobs')
@login_required(role='student')
def student_jobs():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT j.*, c.name AS company_name
                   FROM Jobs j JOIN Companies c ON j.company_id=c.company_id
                   WHERE j.status='Active' AND j.deadline>=CURDATE()
                   ORDER BY j.deadline ASC""")
    jobs = cur.fetchall()
    # Get student cgpa
    cur.execute("SELECT cgpa FROM Students WHERE student_id=%s", (session['user_id'],))
    student = cur.fetchone()
    # Already applied jobs
    cur.execute("SELECT job_id FROM Applications WHERE student_id=%s", (session['user_id'],))
    applied_ids = [row['job_id'] for row in cur.fetchall()]
    cur.close(); db.close()
    return render_template('student_jobs.html', jobs=jobs,
                           student_cgpa=student['cgpa'], applied_ids=applied_ids)


@app.route('/student/apply/<int:job_id>', methods=['POST'])
@login_required(role='student')
def student_apply(job_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    sid = session['user_id']
    # Check eligibility
    cur.execute("SELECT cgpa FROM Students WHERE student_id=%s", (sid,))
    student = cur.fetchone()
    cur.execute("SELECT eligibility_cgpa, deadline, status FROM Jobs WHERE job_id=%s", (job_id,))
    job = cur.fetchone()
    if not job:
        flash('Job not found.', 'danger')
    elif job['status'] == 'Closed':
        flash('This drive is closed.', 'warning')
    elif student['cgpa'] < job['eligibility_cgpa']:
        flash(f'Not eligible. Minimum CGPA required: {job["eligibility_cgpa"]}', 'warning')
    else:
        try:
            cur.execute("INSERT INTO Applications (student_id, job_id) VALUES (%s,%s)",
                        (sid, job_id))
            db.commit()
            flash('Application submitted successfully!', 'success')
        except Exception:
            db.rollback()
            flash('You have already applied for this job.', 'info')
    cur.close(); db.close()
    return redirect(url_for('student_jobs'))


@app.route('/student/applications')
@login_required(role='student')
def student_applications():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT a.application_id, a.applied_date, a.status AS app_status,
                          j.job_role, j.package, c.name AS company_name
                   FROM Applications a
                   JOIN Jobs j ON a.job_id=j.job_id
                   JOIN Companies c ON j.company_id=c.company_id
                   WHERE a.student_id=%s
                   ORDER BY a.applied_date DESC""", (session['user_id'],))
    applications = cur.fetchall()
    cur.close(); db.close()
    return render_template('student_applications.html', applications=applications)


@app.route('/student/profile', methods=['GET', 'POST'])
@login_required(role='student')
def student_profile():
    db = get_db(); cur = db.cursor(dictionary=True)
    sid = session['user_id']
    if request.method == 'POST':
        try:
            cur.execute("""UPDATE Students
                           SET first_name=%s, last_name=%s, branch=%s, cgpa=%s, resume_link=%s
                           WHERE student_id=%s""",
                        (request.form['first_name'],
                         request.form.get('last_name', ''),
                         request.form['branch'],
                         request.form['cgpa'],
                         request.form.get('resume_link', ''),
                         sid))
            db.commit()
            session['name'] = request.form['first_name']
            flash('Profile updated.', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Update failed: {e}', 'danger')
    cur.execute("SELECT * FROM Students WHERE student_id=%s", (sid,))
    student = cur.fetchone()
    cur.close(); db.close()
    return render_template('student_profile.html', student=student)


# ══════════════════════════════════════════════════════════════
#  COMPANY ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/company/dashboard')
@login_required(role='company')
def company_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cid = session['user_id']
    cur.execute("SELECT * FROM Jobs WHERE company_id=%s ORDER BY created_at DESC", (cid,))
    jobs = cur.fetchall()
    # Stats
    cur.execute("SELECT COUNT(*) AS cnt FROM Jobs WHERE company_id=%s", (cid,))
    job_count = cur.fetchone()['cnt']
    cur.execute("""SELECT COUNT(*) AS cnt FROM Applications a
                   JOIN Jobs j ON a.job_id=j.job_id WHERE j.company_id=%s""", (cid,))
    total_apps = cur.fetchone()['cnt']
    cur.close(); db.close()
    return render_template('company_dashboard.html', jobs=jobs,
                           job_count=job_count, total_apps=total_apps)


@app.route('/company/post_job', methods=['GET', 'POST'])
@login_required(role='company')
def post_job():
    if request.method == 'POST':
        db = get_db(); cur = db.cursor()
        try:
            cur.execute(
                """INSERT INTO Jobs
                   (company_id, job_role, description, package, eligibility_cgpa, deadline)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (session['user_id'],
                 request.form['job_role'],
                 request.form.get('description', ''),
                 request.form['package'],
                 request.form.get('eligibility_cgpa', 0),
                 request.form['deadline'])
            )
            db.commit()
            flash('Job posted successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Failed to post job: {e}', 'danger')
        finally:
            cur.close(); db.close()
        return redirect(url_for('company_dashboard'))
    return render_template('post_job.html')


@app.route('/company/applicants/<int:job_id>')
@login_required(role='company')
def view_applicants(job_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    # Verify this job belongs to logged‑in company
    cur.execute("SELECT * FROM Jobs WHERE job_id=%s AND company_id=%s",
                (job_id, session['user_id']))
    job = cur.fetchone()
    if not job:
        flash('Job not found or unauthorized.', 'danger')
        cur.close(); db.close()
        return redirect(url_for('company_dashboard'))
    cur.execute("""SELECT a.application_id, a.status AS app_status, a.applied_date,
                          s.student_id, s.roll_number, s.first_name, s.last_name,
                          s.email, s.branch, s.cgpa, s.resume_link
                   FROM Applications a
                   JOIN Students s ON a.student_id=s.student_id
                   WHERE a.job_id=%s
                   ORDER BY a.applied_date DESC""", (job_id,))
    applicants = cur.fetchall()
    cur.close(); db.close()
    return render_template('view_applicants.html', job=job, applicants=applicants)


@app.route('/company/update_status/<int:app_id>/<status>')
@login_required(role='company')
def update_app_status(app_id, status):
    if status not in ('Selected', 'Rejected'):
        flash('Invalid status.', 'danger')
        return redirect(url_for('company_dashboard'))
    db = get_db(); cur = db.cursor(dictionary=True)
    # Verify ownership
    cur.execute("""SELECT a.job_id FROM Applications a
                   JOIN Jobs j ON a.job_id=j.job_id
                   WHERE a.application_id=%s AND j.company_id=%s""",
                (app_id, session['user_id']))
    row = cur.fetchone()
    if not row:
        flash('Unauthorized.', 'danger')
        cur.close(); db.close()
        return redirect(url_for('company_dashboard'))
    cur.execute("UPDATE Applications SET status=%s WHERE application_id=%s",
                (status, app_id))
    db.commit()
    flash(f'Applicant marked as {status}.', 'success')
    job_id = row['job_id']
    cur.close(); db.close()
    return redirect(url_for('view_applicants', job_id=job_id))


# ══════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS cnt FROM Students")
    total_students = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM Companies")
    total_companies = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM Jobs WHERE status='Active'")
    active_jobs = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM Applications WHERE status='Selected'")
    placed = cur.fetchone()['cnt']
    # Branch-wise stats
    cur.execute("""SELECT s.branch, COUNT(a.application_id) AS placed_count
                   FROM Applications a
                   JOIN Students s ON a.student_id=s.student_id
                   WHERE a.status='Selected'
                   GROUP BY s.branch""")
    branch_stats = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           total_companies=total_companies,
                           active_jobs=active_jobs, placed=placed,
                           branch_stats=branch_stats)


@app.route('/admin/students')
@login_required(role='admin')
def admin_students():
    db = get_db(); cur = db.cursor(dictionary=True)
    search = request.args.get('search', '')
    if search:
        cur.execute("""SELECT * FROM Students
                       WHERE first_name LIKE %s OR roll_number LIKE %s OR branch LIKE %s
                       ORDER BY first_name""",
                    (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute("SELECT * FROM Students ORDER BY first_name")
    students = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin_students.html', students=students, search=search)


@app.route('/admin/companies')
@login_required(role='admin')
def admin_companies():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM Companies ORDER BY name")
    companies = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin_companies.html', companies=companies)


@app.route('/admin/jobs')
@login_required(role='admin')
def admin_jobs():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT j.*, c.name AS company_name
                   FROM Jobs j JOIN Companies c ON j.company_id=c.company_id
                   ORDER BY j.created_at DESC""")
    jobs = cur.fetchall()
    cur.close(); db.close()
    return render_template('admin_jobs.html', jobs=jobs)


@app.route('/admin/delete_job/<int:job_id>')
@login_required(role='admin')
def admin_delete_job(job_id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM Jobs WHERE job_id=%s", (job_id,))
    db.commit()
    flash('Job deleted.', 'info')
    cur.close(); db.close()
    return redirect(url_for('admin_jobs'))


@app.route('/admin/reports')
@login_required(role='admin')
def admin_reports():
    db = get_db(); cur = db.cursor(dictionary=True)
    # Company-wise placement
    cur.execute("""SELECT c.name, COUNT(a.application_id) AS total_hired
                   FROM Applications a
                   JOIN Jobs j ON a.job_id=j.job_id
                   JOIN Companies c ON j.company_id=c.company_id
                   WHERE a.status='Selected'
                   GROUP BY c.name ORDER BY total_hired DESC""")
    company_stats = cur.fetchall()
    # Branch-wise placement
    cur.execute("""SELECT s.branch, COUNT(a.application_id) AS placed
                   FROM Applications a
                   JOIN Students s ON a.student_id=s.student_id
                   WHERE a.status='Selected'
                   GROUP BY s.branch ORDER BY placed DESC""")
    branch_stats = cur.fetchall()
    # Overall
    cur.execute("SELECT COUNT(*) AS cnt FROM Students")
    total_students = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(DISTINCT student_id) AS cnt FROM Applications WHERE status='Selected'")
    placed_students = cur.fetchone()['cnt']
    cur.close(); db.close()
    pct = round((placed_students / total_students * 100), 1) if total_students else 0
    return render_template('admin_reports.html',
                           company_stats=company_stats,
                           branch_stats=branch_stats,
                           total_students=total_students,
                           placed_students=placed_students,
                           placement_pct=pct)


# 
if __name__ == '__main__':
    app.run(debug=True, port=5000)
   
