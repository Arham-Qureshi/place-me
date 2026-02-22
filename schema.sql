
CREATE DATABASE IF NOT EXISTS placement_system;
USE placement_system;

CREATE TABLE IF NOT EXISTS Administrator (
    admin_id    INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Students (
    student_id  INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20)  NOT NULL UNIQUE,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  DEFAULT '',
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    branch      VARCHAR(50)  NOT NULL,
    cgpa        DECIMAL(4,2) DEFAULT 0.00,
    resume_link VARCHAR(255) DEFAULT '',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cgpa CHECK (cgpa >= 0 AND cgpa <= 10)
);

CREATE TABLE IF NOT EXISTS Companies (
    company_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    website     VARCHAR(100) DEFAULT '',
    location    VARCHAR(100) DEFAULT '',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Jobs (
    job_id           INT AUTO_INCREMENT PRIMARY KEY,
    company_id       INT          NOT NULL,
    job_role         VARCHAR(100) NOT NULL,
    description      TEXT         DEFAULT '',
    package          INT          NOT NULL,
    eligibility_cgpa DECIMAL(4,2) DEFAULT 0.00,
    deadline         DATE         NOT NULL,
    status           ENUM('Active', 'Closed') DEFAULT 'Active',
    created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    job_id         INT NOT NULL,
    applied_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    status         ENUM('Applied', 'Selected', 'Rejected') DEFAULT 'Applied',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id)     REFERENCES Jobs(job_id)         ON DELETE CASCADE,
    UNIQUE KEY unique_application (student_id, job_id)
);

CREATE INDEX idx_students_branch ON Students(branch);
CREATE INDEX idx_jobs_status     ON Jobs(status);
CREATE INDEX idx_jobs_deadline   ON Jobs(deadline);
CREATE INDEX idx_app_status      ON Applications(status);

CREATE OR REPLACE VIEW View_Active_Drives AS
SELECT j.job_id, c.name AS company_name, j.job_role, j.package,
       j.eligibility_cgpa, j.deadline
FROM Jobs j
JOIN Companies c ON j.company_id = c.company_id
WHERE j.status = 'Active' AND j.deadline >= CURDATE();

CREATE OR REPLACE VIEW View_Placement_Stats AS
SELECT c.name AS company_name, j.job_role, COUNT(a.application_id) AS total_selected
FROM Applications a
JOIN Jobs j ON a.job_id = j.job_id
JOIN Companies c ON j.company_id = c.company_id
WHERE a.status = 'Selected'
GROUP BY c.name, j.job_role;

DELIMITER //
CREATE TRIGGER trg_close_expired_jobs
BEFORE INSERT ON Applications
FOR EACH ROW
BEGIN
    DECLARE job_deadline DATE;
    SELECT deadline INTO job_deadline FROM Jobs WHERE job_id = NEW.job_id;
    IF job_deadline < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot apply: this job drive has expired.';
    END IF;
END //
DELIMITER ;

INSERT INTO Administrator (username, password) VALUES ('admin', 'admin123');
