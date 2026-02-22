# Project Plan: Placement Management System (PMS)

**Tier-3 Architecture | DBMS Academic Project | 4-6 Weeks Timeline**

---

## 1. Project Overview

### Purpose

The **Placement Management System (PMS)** is a web-based application designed to streamline the campus recruitment process. It bridges the gap between students, companies, and the college placement cell (Admin). The system replaces manual spreadsheets and paperwork with a centralized, database-driven platform.

### Problem Solved

- Eliminates manual data entry errors and redundancy.
- Provides real-time updates on job postings and application status.
- Centralizes student data for easy access by recruiters and admins.
- Automates eligibility checking (based on GPA/Criteria).

### Target Users

1. **Student**: Register, view jobs, apply, track status.
2. **Company (Recruiter)**: Register, post jobs, view applicants (limited), see selected students.
3. **Admin (Placement Cell)**: Manage students/companies, schedule drives, generate reports, approve users.

### Learning Outcomes (DBMS Focus)

- Database Normalization (3NF).
- Complex SQL Queries (Joins, Aggregations).
- Data Integrity & Constraints.
- Transaction Management.
- Connecting a Web Application (Python Flask) to a Relational Database (MySQL).

---

## 2. System Architecture

### 3-Tier Architecture

This project follows a classic **3-Tier Architecture**, ensuring separation of concerns:

1. **Presentation Layer (Frontend)**:

   - **Tech**: HTML5, CSS3, Bootstrap 5.
   - **Role**: Displays UI to users, collects inputs, shows data tables.
   - **Reason**: Bootstrap ensures a responsive, professional look with minimal custom CSS.
2. **Application Layer (Backend)**:

   - **Tech**: Python (Flask Framework).
   - **Role**: Processes logic (e.g., "Is student GPA > Job Criteria?"), handles routing, authentication, and communicates with the DB.
   - **Reason**: Flask is lightweight, easy to learn, and perfect for academic projects.
3. **Data Layer (Database)**:

   - **Tech**: MySQL.
   - **Role**: Stores persistent data (Students, Jobs, Applications).
   - **Reason**: Standard for relational data, supports complex constraints and ACID properties.

### Data Flow

`User (Browser)` <--> `Flask Routes (Logic)` <--> `MySQL Connector` <--> `Database (Storage)`

---

## 3. Functional Modules

### A. Student Module

- **Registration/Login**: Secure access.
- **Profile Management**: Update academic details (CGPA, Branch), upload Resume link.
- **Browse Jobs**: View active placement drives.
- **Apply**: One-click apply (if eligible).
- **My Applications**: Track status (Applied -> Shortlisted -> Selected/Rejected).

### B. Company Module

- **Registration**: Company details, HR contact.
- **Post Jobs**: Job title, description, eligibility (min CGPA), package (CTC).
- **View Applicants**: See list of students who applied to their jobs.

### C. Admin Module

- **Dashboard**: Stats (Total Students, Active Drives, Placed Students).
- **Approve Users**: Verify student/company registrations.
- **Manage Drives**: Edit/Delete job postings if needed.
- **Reports**: Export placement data (e.g., "List of students placed in Infosys").

---

## 4. Database Design (Crucial for DBMS Project)

### Entities & Relationships

- **Student** (N) <---> (1) **Department** (Optional normalization)
- **Company** (1) <---> (N) **Job**
- **Student** (M) <---> (N) **Job** (Through **Application** table)

### Schema (Normalized to 3NF)

#### 1. `Users` (Authentication Table - Optional, or kept separate)

*Centralized login table or separate per role. For simplicity, we use separate tables for this academic project.*

#### 1. `Administrator`

| Attribute    | Type         | Constraints      | Description     |
| :----------- | :----------- | :--------------- | :-------------- |
| `admin_id` | INT          | PK, Auto Inc     | Unique ID       |
| `username` | VARCHAR(50)  | UNIQUE, NOT NULL | Login ID        |
| `password` | VARCHAR(255) | NOT NULL         | Hashed Password |

#### 2. `Students`

| Attribute       | Type         | Constraints        | Description          |
| :-------------- | :----------- | :----------------- | :------------------- |
| `student_id`  | INT          | PK, Auto Inc       | Internal Ref         |
| `roll_number` | VARCHAR(20)  | UNIQUE, NOT NULL   | College Roll No      |
| `first_name`  | VARCHAR(50)  | NOT NULL           |                      |
| `last_name`   | VARCHAR(50)  |                    |                      |
| `email`       | VARCHAR(100) | UNIQUE, NOT NULL   |                      |
| `password`    | VARCHAR(255) | NOT NULL           |                      |
| `branch`      | VARCHAR(50)  | NOT NULL           | CSE, ECE, MECH...    |
| `cgpa`        | DECIMAL(4,2) | CHECK (cgpa <= 10) | Current CGPA         |
| `resume_link` | VARCHAR(255) |                    | GDrive/LinkedIn Link |

#### 3. `Companies`

| Attribute      | Type         | Constraints      | Description    |
| :------------- | :----------- | :--------------- | :------------- |
| `company_id` | INT          | PK, Auto Inc     |                |
| `name`       | VARCHAR(100) | UNIQUE, NOT NULL | e.g., "Google" |
| `email`      | VARCHAR(100) | UNIQUE, NOT NULL | HR Email       |
| `password`   | VARCHAR(255) | NOT NULL         |                |
| `website`    | VARCHAR(100) |                  |                |
| `location`   | VARCHAR(100) |                  | HQ Location    |

#### 4. `Jobs` (Placement Drives)

| Attribute            | Type         | Constraints        | Description        |
| :------------------- | :----------- | :----------------- | :----------------- |
| `job_id`           | INT          | PK, Auto Inc       |                    |
| `company_id`       | INT          | FK -> Companies.id | Posting Company    |
| `job_role`         | VARCHAR(100) | NOT NULL           | e.g., "SDE-1"      |
| `package`          | INT          | NOT NULL           | CTC in LPA         |
| `eligibility_cgpa` | DECIMAL(4,2) | DEFAULT 0.0        | Min CGPA required  |
| `deadline`         | DATE         | NOT NULL           | Last date to apply |
| `status`           | ENUM         | 'Active', 'Closed' | Drive Status       |

#### 5. `Applications` (Connecting Table)

| Attribute          | Type     | Constraints                       | Description    |
| :----------------- | :------- | :-------------------------------- | :------------- |
| `application_id` | INT      | PK, Auto Inc                      |                |
| `student_id`     | INT      | FK -> Students.id                 | Who applied?   |
| `job_id`         | INT      | FK -> Jobs.id                     | Which job?     |
| `applied_date`   | DATETIME | DEFAULT NOW()                     | Timestamp      |
| `status`         | ENUM     | 'Applied', 'Selected', 'Rejected' | Current Status |

### Constraints & Integrity

- **Primary Keys**: Uniquely identify records.
- **Foreign Keys**: `company_id` in `Jobs`, `student_id`/`job_id` in `Applications`. Enforce `ON DELETE CASCADE` where appropriate.
- **Unique**: Email, Roll Number.
- **Check**: `cgpa >= 0 AND cgpa <= 10`.

---

## 5. Core SQL Operations

### A. Major Queries (CRUD)

1. **Register Student**:
   ```sql
   INSERT INTO Students (roll_number, first_name, email, password, branch, cgpa)
   VALUES ('CS101', 'Rahul', 'rahul@mail.com', 'hashed_pass', 'CSE', 8.5);
   ```
2. **Post a Job**:
   ```sql
   INSERT INTO Jobs (company_id, job_role, package, eligibility_cgpa, deadline)
   VALUES (1, 'Data Analyst', 600000, 7.0, '2023-12-31');
   ```
3. **Apply for Job**:
   ```sql
   INSERT INTO Applications (student_id, job_id, status) VALUES (5, 2, 'Applied');
   ```

### B. Complex Joins

1. **View All Applications for a Company**:
   ```sql
   SELECT s.first_name, s.email, s.cgpa, s.resume_link
   FROM Students s
   JOIN Applications a ON s.student_id = a.student_id
   JOIN Jobs j ON a.job_id = j.job_id
   WHERE j.company_id = 1 AND j.job_id = 10;
   ```
2. **Student's Dashboard (My Applications)**:
   ```sql
   SELECT c.name, j.job_role, j.package, a.status
   FROM Applications a
   JOIN Jobs j ON a.job_id = j.job_id
   JOIN Companies c ON j.company_id = c.company_id
   WHERE a.student_id = 5;
   ```

### C. Analytics (Aggregation)

1. **Count Placed Students per Company**:
   ```sql
   SELECT c.name, COUNT(a.student_id) as total_hired
   FROM Companies c
   JOIN Jobs j ON c.company_id = j.company_id
   JOIN Applications a ON j.job_id = a.job_id
   WHERE a.status = 'Selected'
   GROUP BY c.name;
   ```

### D. Views

- `View_Active_Drives`: Pre-filter jobs where `deadline >= TODAY`.

---

## 6. Frontend UI Design

*Professional, Clean, "University Portal" Style*

- **Color Palette**:
  - Primary: Royal Blue (`#0056b3`) or Teal (`#008080`)
  - Background: Off-white (`#f8f9fa`)
  - Text: Dark Grey (`#333`)
  - Success/Action Buttons: Green (`#28a745`)
- **Layout**:
  - **Navbar**: Logo left, Links (Home, Jobs, Profile, Logout) right.
  - **Cards**: For Job postings (Company Logo + Role + Package).
  - **Tables**: Striped Bootstrap tables for lists (Applicants/Jobs).
  - **Footer**: Copyright & Links.

---

## 7. Frontend Pages Plan

1. **Common**:

   - `index.html`: Landing page (Login buttons for Student/Admin/Company).
   - `register.html`: Tabbed form for Student/Company registration.
2. **Student Pages**:

   - `student_dashboard.html`: Summary of eligible jobs, recent notices.
   - `jobs_list.html`: Grid of available job cards with "Apply" buttons.
   - `my_applications.html`: Table showing applied jobs and status.
   - `student_profile.html`: Edit personal details.
3. **Company Pages**:

   - `company_dashboard.html`: Active jobs posted by them.
   - `post_job.html`: Form to create a new drive.
   - `view_applicants.html`: Table of students who applied for a specific job.
4. **Admin Pages**:

   - `admin_dashboard.html`: Stats overview.
   - `manage_companies.html`: List/Approve companies.
   - `manage_students.html`: View/Search students.

---

## 8. Backend (Flask) Structure

```text
/placement_system
    /static
        /css        # style.css
        /images     # logos
    /templates      # HTML files
        index.html
        student_dashboard.html
        ...
    app.py          # Main Flask Application
    db_config.py    # Database connection string
    routes.py       # (Optional) Separated routes
```

### Key Logic

- **Decorator**: `@login_required` to protect dashboard routes.
- **Session**: Store `user_id` and `role` in `session` (Flask-Session).
- **DB Connection**: Use `mysql-connector-python` or `SQLAlchemy`.

---

## 9. Implementation Timeline (4-6 Weeks)

| Week        | Phase                    | Milestones                                                 |
| :---------- | :----------------------- | :--------------------------------------------------------- |
| **1** | **Planning & DB**  | Requirement gathering, ER Diagram, Create Tables in MySQL. |
| **2** | **Backend Setup**  | Set up Flask, connect DB, implement Login/Register logic.  |
| **3** | **Student Module** | Build Profile, Job Listing, and Apply functionality.       |
| **4** | **Company Module** | Build Job Posting and Applicant Viewing.                   |
| **5** | **Admin & Polish** | Admin dashboard, report generation, UI cleanup (CSS).      |
| **6** | **Testing & Doc**  | Test all flows, write Project Report, Prepare for Viva.    |

---

## 10. Testing & Validation

### Sample Test Cases

1. **Login**: Enter invalid password -> Show "Invalid Credentials".
2. **Job Application**:
   - Student with CGPA 6.0 applies for Job needing 7.0 -> **Block Action** ("Not Eligible").
   - Student applies twice to same job -> **Prevent Duplicate**.
3. **Data View**: Company A should NOT see details of Company B.

---

## 11. Documentation for Submission

### Report Sections

1. **Abstract**: 1-page summary.
2. **ER Diagram**: Visual representation of tables.
3. **Schema Diagram**: Table structures with keys.
4. **Source Code**: Backend and SQL scripts.
5. **Screenshots**: Printouts of every page.
6. **Conclusion & Future Scope**.

### Viva Questions

- *Why did you use 3NF?* (To reduce redundancy).
- *Explain the join used in the 'My Applications' page.*
- *How do you handle SQL Injection?* (Use parameterized queries).

---

## 12. Future Enhancements

(Mention these in your report as "Future Scope")

- Resume PDF parsing/upload.
- Email notifications for selection.
- Alumni connection portal.
