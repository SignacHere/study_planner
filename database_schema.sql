-- AI-Based Study Planner - Database Schema
-- SQLite compatible schema with comprehensive tables for the system

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    daily_study_hours REAL DEFAULT 4.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SUBJECTS TABLE
-- ============================================
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_name VARCHAR(150) NOT NULL,
    difficulty_level VARCHAR(20) CHECK(difficulty_level IN ('easy', 'medium', 'hard')),
    difficulty_score INTEGER DEFAULT 2 CHECK(difficulty_score BETWEEN 1 AND 3),
    importance_weight REAL DEFAULT 1.0,
    total_topics INTEGER DEFAULT 0,
    completed_topics INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, subject_name)
);

-- ============================================
-- EXAMS TABLE
-- ============================================
CREATE TABLE exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_date DATE NOT NULL,
    exam_time TIME,
    exam_type VARCHAR(50) DEFAULT 'regular',
    duration_minutes INTEGER,
    syllabus_coverage TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

-- ============================================
-- STUDY SCHEDULE TABLE
-- ============================================
CREATE TABLE study_schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    study_date DATE NOT NULL,
    planned_hours REAL NOT NULL,
    actual_hours REAL DEFAULT 0,
    priority_score REAL NOT NULL,
    session_type VARCHAR(50) DEFAULT 'study' CHECK(session_type IN ('study', 'revision', 'practice', 'buffer')),
    topics_to_cover TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'skipped')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE(user_id, subject_id, study_date)
);

-- ============================================
-- PROGRESS TRACKING TABLE
-- ============================================
CREATE TABLE progress_tracking (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    date DATE NOT NULL,
    hours_studied REAL NOT NULL,
    topics_completed TEXT,
    confidence_level INTEGER CHECK(confidence_level BETWEEN 1 AND 5),
    difficulties_faced TEXT,
    self_rating INTEGER CHECK(self_rating BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

-- ============================================
-- STUDY SESSIONS TABLE
-- ============================================
CREATE TABLE study_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    session_type VARCHAR(50),
    productivity_rating INTEGER CHECK(productivity_rating BETWEEN 1 AND 5),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

-- ============================================
-- ADAPTIVE ADJUSTMENTS TABLE
-- ============================================
CREATE TABLE adaptive_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    adjustment_date DATE NOT NULL,
    reason VARCHAR(255),
    subjects_affected TEXT,
    old_schedule_data TEXT,
    new_schedule_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_subjects_user ON subjects(user_id);
CREATE INDEX idx_exams_user ON exams(user_id);
CREATE INDEX idx_exams_date ON exams(exam_date);
CREATE INDEX idx_schedule_user_date ON study_schedule(user_id, study_date);
CREATE INDEX idx_schedule_subject ON study_schedule(subject_id);
CREATE INDEX idx_progress_user_date ON progress_tracking(user_id, date);
CREATE INDEX idx_sessions_user ON study_sessions(user_id);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Upcoming exams with subject details
CREATE VIEW upcoming_exams AS
SELECT 
    e.exam_id,
    e.user_id,
    s.subject_name,
    s.difficulty_level,
    e.exam_date,
    e.exam_time,
    CAST((JULIANDAY(e.exam_date) - JULIANDAY('now')) AS INTEGER) as days_remaining
FROM exams e
JOIN subjects s ON e.subject_id = s.subject_id
WHERE e.exam_date >= DATE('now')
ORDER BY e.exam_date;

-- View: Daily schedule with subject info
CREATE VIEW daily_schedule_view AS
SELECT 
    ss.schedule_id,
    ss.user_id,
    ss.study_date,
    s.subject_name,
    s.difficulty_level,
    ss.planned_hours,
    ss.actual_hours,
    ss.priority_score,
    ss.session_type,
    ss.status,
    ss.topics_to_cover
FROM study_schedule ss
JOIN subjects s ON ss.subject_id = s.subject_id
ORDER BY ss.study_date, ss.priority_score DESC;

-- View: Subject progress summary
CREATE VIEW subject_progress_summary AS
SELECT 
    s.subject_id,
    s.user_id,
    s.subject_name,
    s.difficulty_level,
    s.total_topics,
    s.completed_topics,
    ROUND(CAST(s.completed_topics AS REAL) / NULLIF(s.total_topics, 0) * 100, 2) as completion_percentage,
    COALESCE(SUM(pt.hours_studied), 0) as total_hours_studied,
    COALESCE(AVG(pt.confidence_level), 0) as avg_confidence
FROM subjects s
LEFT JOIN progress_tracking pt ON s.subject_id = pt.subject_id
GROUP BY s.subject_id;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Insert sample user
INSERT INTO users (username, email, password_hash, daily_study_hours) 
VALUES ('john_doe', 'john@example.com', 'hashed_password_here', 5.0);

-- Insert sample subjects
INSERT INTO subjects (user_id, subject_name, difficulty_level, difficulty_score, importance_weight, total_topics) 
VALUES 
    (1, 'Mathematics', 'hard', 3, 1.5, 15),
    (1, 'Physics', 'hard', 3, 1.3, 12),
    (1, 'Chemistry', 'medium', 2, 1.2, 10),
    (1, 'English', 'easy', 1, 1.0, 8),
    (1, 'Computer Science', 'medium', 2, 1.4, 10);

-- Insert sample exams
INSERT INTO exams (user_id, subject_id, exam_date, exam_time) 
VALUES 
    (1, 1, DATE('now', '+15 days'), '09:00:00'),
    (1, 2, DATE('now', '+18 days'), '09:00:00'),
    (1, 3, DATE('now', '+22 days'), '09:00:00'),
    (1, 4, DATE('now', '+25 days'), '09:00:00'),
    (1, 5, DATE('now', '+28 days'), '09:00:00');
