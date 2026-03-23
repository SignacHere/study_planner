# AI-Based Study Planner

An intelligent study planning system that generates personalized daily study schedules based on exam timetables, subject difficulty, and available preparation time.

## 🎯 Features

- **Smart Priority Calculation**: Uses the formula `Priority = (Difficulty × Weight × Urgency) / Days Remaining`
- **Automated Schedule Generation**: Creates optimized daily study plans
- **Adaptive Learning**: Adjusts schedules based on user progress
- **Subject Management**: Add and track multiple subjects with difficulty levels
- **Exam Tracking**: Monitor upcoming exams and preparation time
- **Progress Analytics**: View study hours, confidence levels, and performance metrics
- **Beautiful UI**: Modern, responsive web interface

## 📋 System Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Extract or Clone the Project

```bash
cd study_planner
```

### 2. Install Dependencies

```bash
pip install flask flask-cors
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
cd backend
python app.py
```

The server will start at `http://127.0.0.1:5000`

### 4. Open in Browser

Navigate to `http://127.0.0.1:5000` in your web browser.

## 📖 Usage Guide

### Step 1: Add Subjects

1. Fill in the "Add Subject" form:
   - **Subject Name**: e.g., Mathematics, Physics
   - **Difficulty Level**: Easy, Medium, or Hard
   - **Importance Weight**: 0.5 to 2.0 (higher = more important)
   - **Total Topics**: Number of topics to cover

2. Click "Add Subject"

### Step 2: Add Exams

1. Select a subject from the dropdown
2. Choose the exam date
3. Optionally add exam time
4. Click "Add Exam"

### Step 3: Generate Study Schedule

1. Set your daily study hours in Settings
2. Click "🎯 Generate Study Schedule"
3. Your personalized schedule will appear below

### Step 4: Track Progress (Optional)

Use the API endpoint `/api/progress` to log daily progress and trigger adaptive rescheduling.

## 🏗️ Project Structure

```
study_planner/
├── backend/
│   ├── app.py                 # Main Flask application
│   └── templates/
│       └── index.html         # Frontend interface
├── database/
│   └── study_planner.db       # SQLite database (auto-created)
├── requirements.txt           # Python dependencies
├── architecture.md            # System architecture documentation
└── database_schema.sql        # Database schema
```

## 🔧 API Endpoints

### Users
- `POST /api/users` - Create new user

### Subjects
- `GET /api/subjects?user_id=1` - Get all subjects
- `POST /api/subjects` - Add new subject

### Exams
- `GET /api/exams?user_id=1` - Get all exams
- `POST /api/exams` - Add new exam

### Schedule
- `POST /api/schedule/generate` - Generate study schedule
- `GET /api/schedule/all?user_id=1` - Get complete schedule
- `GET /api/schedule/daily/<date>?user_id=1` - Get daily schedule

### Progress
- `POST /api/progress` - Log progress and update schedule

### Analytics
- `GET /api/analytics/dashboard?user_id=1` - Get dashboard stats

## 📊 Database Schema

The system uses SQLite with the following main tables:

- **users**: User accounts and preferences
- **subjects**: Subject information and difficulty
- **exams**: Exam schedules
- **study_schedule**: Generated daily schedules
- **progress_tracking**: User progress logs

See `database_schema.sql` for complete schema.

## 🧮 Priority Algorithm

The system calculates priority using:

```
Priority Score = (Difficulty × Weight × Urgency Factor) / Days Remaining

Where:
- Difficulty: 1 (easy), 2 (medium), 3 (hard)
- Weight: User-defined importance (0.5 - 2.0)
- Urgency Factor: 1 + (1 / max(Days Remaining, 1))
- Days Remaining: Days until exam
```

Higher priority subjects get more study time allocation.

## 🔄 Adaptive Scheduling

The system adapts to user progress:

1. User logs daily progress with confidence level (1-5)
2. System calculates average confidence per subject
3. Struggling subjects (confidence < 3) get increased weight (+20%)
4. Mastered subjects (confidence > 4) get decreased weight (-10%)
5. Schedule regenerates with updated priorities

## 🎨 Customization

### Modify Daily Study Hours
Update in Settings card or via database:
```sql
UPDATE users SET daily_study_hours = 6.0 WHERE user_id = 1;
```

### Adjust Priority Weights
Edit in `backend/app.py`:
```python
def calculate_priority(difficulty_score, importance_weight, days_remaining):
    # Modify this formula as needed
    urgency_factor = 1 + (1 / max(days_remaining, 1))
    priority = (difficulty_score * importance_weight * urgency_factor) / days_remaining
    return round(priority, 4)
```

## 🐛 Troubleshooting

### Database not found
- The database is created automatically on first run
- Ensure the `database/` directory exists

### Port already in use
- Change the port in `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Change 5000 to 5001
  ```

### No subjects in dropdown
- Add subjects first before adding exams
- Refresh the page to reload subjects

### Schedule not generating
- Ensure you have at least one subject and one exam
- Check that exam dates are in the future

## 📈 Future Enhancements

- [ ] Mobile application
- [ ] AI-based difficulty prediction using ML
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Voice assistant support
- [ ] Gamification (rewards, streaks, achievements)
- [ ] Collaborative study groups
- [ ] Pomodoro timer integration
- [ ] Flashcard creation and SRS
- [ ] Performance prediction models

## 🤝 Contributing

This is an educational project. Feel free to:
- Report bugs
- Suggest features
- Improve the algorithm
- Enhance the UI

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Developer

Created as part of an AI-Based Study Planner project.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check database schema
4. Verify all dependencies are installed

## 🌟 Acknowledgments

- Flask framework for backend
- SQLite for database
- Vanilla JavaScript for frontend simplicity
- Modern CSS for beautiful UI

---

**Happy Studying! 📚✨**
