"""
AI-Based Study Planner - Main Application
Flask backend with scheduling algorithms
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import json
import os
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# Database configuration
DB_PATH = 'database/study_planner.db'

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            daily_study_hours REAL DEFAULT 4.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Subjects table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_name VARCHAR(150) NOT NULL,
            difficulty_level VARCHAR(20) CHECK(difficulty_level IN ('easy', 'medium', 'hard')),
            difficulty_score INTEGER DEFAULT 2 CHECK(difficulty_score BETWEEN 1 AND 3),
            importance_weight REAL DEFAULT 1.0,
            total_topics INTEGER DEFAULT 0,
            completed_topics INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, subject_name)
        )
    ''')
    
    # Exams table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            exam_date DATE NOT NULL,
            exam_time TIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
        )
    ''')
    
    # Study schedule table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study_schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            study_date DATE NOT NULL,
            planned_hours REAL NOT NULL,
            actual_hours REAL DEFAULT 0,
            priority_score REAL NOT NULL,
            session_type VARCHAR(50) DEFAULT 'study',
            topics_to_cover TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
        )
    ''')
    
    # Progress tracking table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            date DATE NOT NULL,
            hours_studied REAL NOT NULL,
            confidence_level INTEGER CHECK(confidence_level BETWEEN 1 AND 5),
            self_rating INTEGER CHECK(self_rating BETWEEN 1 AND 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# ============================================
# CORE SCHEDULING ALGORITHMS
# ============================================

def calculate_priority(difficulty_score: int, importance_weight: float, 
                      days_remaining: int) -> float:
    """
    Calculate priority score for a subject
    Priority = (Difficulty × Weight × Urgency Factor) / Days Remaining
    """
    if days_remaining <= 0:
        days_remaining = 1
    
    urgency_factor = 1 + (1 / max(days_remaining, 1))
    priority = (difficulty_score * importance_weight * urgency_factor) / days_remaining
    
    return round(priority, 4)

def generate_study_schedule(user_id: int) -> List[Dict[str, Any]]:
    """
    Generate optimized study schedule based on exams
    """
    conn = get_db_connection()
    
    # Get user's daily study hours
    user = conn.execute('SELECT daily_study_hours FROM users WHERE user_id = ?', 
                       (user_id,)).fetchone()
    if not user:
        return []
    
    daily_hours = user['daily_study_hours']
    
    # Get all upcoming exams with subject details
    exams_query = '''
        SELECT e.exam_id, e.exam_date, e.subject_id,
               s.subject_name, s.difficulty_score, s.importance_weight,
               s.total_topics, s.completed_topics
        FROM exams e
        JOIN subjects s ON e.subject_id = s.subject_id
        WHERE e.user_id = ? AND e.exam_date >= DATE('now')
        ORDER BY e.exam_date
    '''
    
    exams = conn.execute(exams_query, (user_id,)).fetchall()
    
    if not exams:
        return []
    
    schedule = []
    today = datetime.now().date()
    
    # Calculate priorities and days remaining for each exam
    exam_data = []
    for exam in exams:
        exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d').date()
        days_remaining = (exam_date - today).days
        
        priority = calculate_priority(
            exam['difficulty_score'],
            exam['importance_weight'],
            days_remaining
        )
        
        exam_data.append({
            'subject_id': exam['subject_id'],
            'subject_name': exam['subject_name'],
            'exam_date': exam_date,
            'days_remaining': days_remaining,
            'priority': priority,
            'difficulty_score': exam['difficulty_score'],
            'total_topics': exam['total_topics'],
            'completed_topics': exam['completed_topics']
        })
    
    # Sort by priority (descending)
    exam_data.sort(key=lambda x: x['priority'], reverse=True)
    
    # Generate daily schedule until first exam
    first_exam_date = min(exam['exam_date'] for exam in exam_data)
    current_date = today
    
    while current_date < first_exam_date:
        daily_hours_remaining = daily_hours
        daily_schedule = []
        
        # Allocate hours to subjects based on priority
        for exam in exam_data:
            if current_date >= exam['exam_date']:
                continue
            
            days_until_exam = (exam['exam_date'] - current_date).days
            
            # Determine session type
            if days_until_exam <= 2:
                session_type = 'revision'
            elif days_until_exam <= 1:
                session_type = 'buffer'
            else:
                session_type = 'study'
            
            # Calculate hours for this subject
            # Higher priority subjects get more time
            total_priority = sum(e['priority'] for e in exam_data 
                               if current_date < e['exam_date'])
            
            if total_priority > 0:
                subject_hours = (exam['priority'] / total_priority) * daily_hours
                subject_hours = min(subject_hours, daily_hours_remaining, 3.0)  # Max 3 hours per subject
                subject_hours = max(subject_hours, 0.5)  # Min 0.5 hours
                subject_hours = round(subject_hours, 1)
                
                if subject_hours > 0 and daily_hours_remaining > 0:
                    daily_schedule.append({
                        'user_id': user_id,
                        'subject_id': exam['subject_id'],
                        'subject_name': exam['subject_name'],
                        'study_date': current_date.isoformat(),
                        'planned_hours': subject_hours,
                        'priority_score': exam['priority'],
                        'session_type': session_type,
                        'status': 'pending'
                    })
                    
                    daily_hours_remaining -= subject_hours
        
        schedule.extend(daily_schedule)
        current_date += timedelta(days=1)
    
    # Save schedule to database
    conn.execute('DELETE FROM study_schedule WHERE user_id = ?', (user_id,))
    
    for entry in schedule:
        conn.execute('''
            INSERT INTO study_schedule 
            (user_id, subject_id, study_date, planned_hours, priority_score, session_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry['user_id'], entry['subject_id'], entry['study_date'],
              entry['planned_hours'], entry['priority_score'], 
              entry['session_type'], entry['status']))
    
    conn.commit()
    conn.close()
    
    return schedule

def adapt_schedule(user_id: int, subject_id: int, progress_data: Dict[str, Any]):
    """
    Adapt schedule based on user progress
    """
    conn = get_db_connection()
    
    # Log progress
    conn.execute('''
        INSERT INTO progress_tracking 
        (user_id, subject_id, date, hours_studied, confidence_level, self_rating)
        VALUES (?, ?, DATE('now'), ?, ?, ?)
    ''', (user_id, subject_id, progress_data.get('hours_studied', 0),
          progress_data.get('confidence_level', 3), 
          progress_data.get('self_rating', 5)))
    
    # Get average confidence for subject
    avg_confidence = conn.execute('''
        SELECT AVG(confidence_level) as avg_conf
        FROM progress_tracking
        WHERE user_id = ? AND subject_id = ?
    ''', (user_id, subject_id)).fetchone()['avg_conf']
    
    # Adjust importance weight based on confidence
    if avg_confidence and avg_confidence < 3:
        # Struggling with this subject - increase weight
        conn.execute('''
            UPDATE subjects
            SET importance_weight = importance_weight * 1.2
            WHERE user_id = ? AND subject_id = ?
        ''', (user_id, subject_id))
    elif avg_confidence and avg_confidence > 4:
        # Doing well - can decrease weight slightly
        conn.execute('''
            UPDATE subjects
            SET importance_weight = MAX(importance_weight * 0.9, 0.8)
            WHERE user_id = ? AND subject_id = ?
        ''', (user_id, subject_id))
    
    conn.commit()
    conn.close()
    
    # Regenerate schedule with updated weights
    return generate_study_schedule(user_id)

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            INSERT INTO users (username, email, daily_study_hours)
            VALUES (?, ?, ?)
        ''', (data['username'], data['email'], data.get('daily_study_hours', 4.0)))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User created successfully'
        }), 201
    except sqlite3.IntegrityError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/subjects', methods=['GET', 'POST'])
def subjects():
    """Get all subjects or create new subject"""
    conn = get_db_connection()
    
    if request.method == 'GET':
        user_id = request.args.get('user_id', 1)
        subjects = conn.execute('''
            SELECT * FROM subjects WHERE user_id = ?
        ''', (user_id,)).fetchall()
        
        conn.close()
        return jsonify([dict(s) for s in subjects])
    
    elif request.method == 'POST':
        data = request.json
        
        # Map difficulty level to score
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        difficulty_score = difficulty_map.get(data['difficulty_level'], 2)
        
        try:
            cursor = conn.execute('''
                INSERT INTO subjects 
                (user_id, subject_name, difficulty_level, difficulty_score, 
                 importance_weight, total_topics)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['user_id'], data['subject_name'], data['difficulty_level'],
                  difficulty_score, data.get('importance_weight', 1.0),
                  data.get('total_topics', 0)))
            
            conn.commit()
            subject_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'subject_id': subject_id,
                'message': 'Subject added successfully'
            }), 201
        except sqlite3.IntegrityError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            conn.close()

@app.route('/api/exams', methods=['GET', 'POST'])
def exams():
    """Get all exams or create new exam"""
    conn = get_db_connection()
    
    if request.method == 'GET':
        user_id = request.args.get('user_id', 1)
        exams_query = '''
            SELECT e.*, s.subject_name, s.difficulty_level
            FROM exams e
            JOIN subjects s ON e.subject_id = s.subject_id
            WHERE e.user_id = ?
            ORDER BY e.exam_date
        '''
        exams = conn.execute(exams_query, (user_id,)).fetchall()
        
        conn.close()
        return jsonify([dict(e) for e in exams])
    
    elif request.method == 'POST':
        data = request.json
        
        try:
            cursor = conn.execute('''
                INSERT INTO exams (user_id, subject_id, exam_date, exam_time)
                VALUES (?, ?, ?, ?)
            ''', (data['user_id'], data['subject_id'], data['exam_date'],
                  data.get('exam_time')))
            
            conn.commit()
            exam_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'exam_id': exam_id,
                'message': 'Exam added successfully'
            }), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            conn.close()

@app.route('/api/schedule/generate', methods=['POST'])
def generate_schedule():
    """Generate study schedule for user"""
    data = request.json
    user_id = data.get('user_id', 1)
    
    schedule = generate_study_schedule(user_id)
    
    return jsonify({
        'success': True,
        'schedule': schedule,
        'total_days': len(set(s['study_date'] for s in schedule)),
        'message': 'Schedule generated successfully'
    })

@app.route('/api/schedule/daily/<date>')
def get_daily_schedule(date):
    """Get schedule for a specific date"""
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    
    query = '''
        SELECT ss.*, s.subject_name, s.difficulty_level
        FROM study_schedule ss
        JOIN subjects s ON ss.subject_id = s.subject_id
        WHERE ss.user_id = ? AND ss.study_date = ?
        ORDER BY ss.priority_score DESC
    '''
    
    schedule = conn.execute(query, (user_id, date)).fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in schedule])

@app.route('/api/schedule/all')
def get_all_schedule():
    """Get complete schedule"""
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    
    query = '''
        SELECT ss.*, s.subject_name, s.difficulty_level
        FROM study_schedule ss
        JOIN subjects s ON ss.subject_id = s.subject_id
        WHERE ss.user_id = ?
        ORDER BY ss.study_date, ss.priority_score DESC
    '''
    
    schedule = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in schedule])

@app.route('/api/progress', methods=['POST'])
def log_progress():
    """Log daily progress and adapt schedule"""
    data = request.json
    user_id = data['user_id']
    subject_id = data['subject_id']
    
    progress_data = {
        'hours_studied': data.get('hours_studied', 0),
        'confidence_level': data.get('confidence_level', 3),
        'self_rating': data.get('self_rating', 5)
    }
    
    # Adapt schedule based on progress
    new_schedule = adapt_schedule(user_id, subject_id, progress_data)
    
    return jsonify({
        'success': True,
        'message': 'Progress logged and schedule updated',
        'schedule_updated': len(new_schedule) > 0
    })

@app.route('/api/analytics/dashboard')
def get_analytics():
    """Get analytics dashboard data"""
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    
    # Total study hours
    total_hours = conn.execute('''
        SELECT SUM(hours_studied) as total
        FROM progress_tracking
        WHERE user_id = ?
    ''', (user_id,)).fetchone()['total'] or 0
    
    # Subject-wise progress
    subject_progress = conn.execute('''
        SELECT s.subject_name, 
               SUM(pt.hours_studied) as hours,
               AVG(pt.confidence_level) as avg_confidence
        FROM subjects s
        LEFT JOIN progress_tracking pt ON s.subject_id = pt.subject_id
        WHERE s.user_id = ?
        GROUP BY s.subject_id
    ''', (user_id,)).fetchall()
    
    # Upcoming exams
    upcoming_exams = conn.execute('''
        SELECT s.subject_name, e.exam_date,
               CAST((JULIANDAY(e.exam_date) - JULIANDAY('now')) AS INTEGER) as days_left
        FROM exams e
        JOIN subjects s ON e.subject_id = s.subject_id
        WHERE e.user_id = ? AND e.exam_date >= DATE('now')
        ORDER BY e.exam_date
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'total_study_hours': round(total_hours, 1),
        'subject_progress': [dict(s) for s in subject_progress],
        'upcoming_exams': [dict(e) for e in upcoming_exams]
    })

# ============================================
# INITIALIZATION
# ============================================

if __name__ == '__main__':
    # Create database directory if not exists
    os.makedirs('database', exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("=" * 60)
    print("AI-Based Study Planner - Server Starting")
    print("=" * 60)
    print("Database initialized successfully")
    print("Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    
    if __name__ == "__main__":
        app.run()
