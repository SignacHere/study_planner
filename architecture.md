# AI-Based Study Planner - System Architecture

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web App    │  │  Mobile App  │  │  Dashboard   │      │
│  │ (React/HTML) │  │  (Future)    │  │   (Admin)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              REST API (Flask/FastAPI)                │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │   Auth     │  │  Schedule  │  │  Progress  │    │   │
│  │  │  Service   │  │  Service   │  │  Service   │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Priority    │  │  Schedule    │  │  Adaptive    │      │
│  │  Calculator  │  │  Generator   │  │  Engine      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Analytics   │  │  AI Module   │  │  Validator   │      │
│  │  Engine      │  │  (Optional)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   User DAO   │  │  Exam DAO    │  │ Schedule DAO │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            SQLite / MySQL Database                   │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │   │
│  │  │ Users  │ │ Exams  │ │Schedule│ │Progress│       │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Details

### 2.1 Frontend Components
- **Input Forms**: Exam timetable entry, subject difficulty selection
- **Dashboard**: Visual schedule display, progress tracking
- **Analytics**: Charts for study hours, subject performance
- **Settings**: User preferences, notification management

### 2.2 Backend Services
- **Authentication Service**: User login, registration, session management
- **Schedule Service**: Generate and manage study schedules
- **Progress Service**: Track daily progress and update schedules
- **Analytics Service**: Generate insights and reports

### 2.3 Core Algorithms

#### Priority Calculation Algorithm
```
Priority Score = (Difficulty × Weight × Urgency Factor) / Days Remaining

Where:
- Difficulty: 1 (easy), 2 (medium), 3 (hard)
- Weight: User-defined importance (0.5 - 2.0)
- Urgency Factor: 1 + (1 / max(Days Remaining, 1))
- Days Remaining: Days until exam
```

#### Schedule Generation Algorithm
```
1. Calculate priority for each subject
2. Sort subjects by priority (descending)
3. For each day until first exam:
   a. Allocate available study hours
   b. Distribute hours based on priority
   c. Apply constraints (max hours per subject/day)
   d. Add revision sessions (last 2 days before exam)
4. Generate balanced weekly schedule
5. Include buffer days
```

#### Adaptive Adjustment Algorithm
```
1. Collect daily progress data
2. Calculate actual vs planned completion rate
3. Identify struggling subjects (low confidence/progress)
4. Recalculate priorities:
   - Increase weight for struggling subjects
   - Decrease weight for mastered subjects
5. Regenerate schedule for remaining days
```

## 3. Data Flow

### 3.1 Schedule Generation Flow
```
User Input → Validate Data → Calculate Gaps → 
Compute Priorities → Generate Schedule → Store in DB → 
Display to User
```

### 3.2 Progress Update Flow
```
User Logs Progress → Update Progress Table → 
Trigger Adaptive Engine → Recalculate Priorities → 
Regenerate Schedule → Notify User
```

## 4. API Endpoints Design

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Subjects
- `GET /api/subjects` - Get all subjects
- `POST /api/subjects` - Add new subject
- `PUT /api/subjects/:id` - Update subject
- `DELETE /api/subjects/:id` - Delete subject

### Exams
- `GET /api/exams` - Get all exams
- `POST /api/exams` - Add exam
- `PUT /api/exams/:id` - Update exam
- `DELETE /api/exams/:id` - Delete exam

### Schedule
- `POST /api/schedule/generate` - Generate study schedule
- `GET /api/schedule/daily/:date` - Get daily schedule
- `GET /api/schedule/weekly` - Get weekly schedule
- `PUT /api/schedule/:id` - Update schedule entry

### Progress
- `POST /api/progress` - Log daily progress
- `GET /api/progress/subject/:id` - Get subject progress
- `GET /api/progress/analytics` - Get analytics data

## 5. Technology Stack

### Frontend
- **Framework**: React.js / Vanilla HTML+CSS+JS
- **UI Library**: Bootstrap / Tailwind CSS
- **Charts**: Chart.js / Recharts
- **State Management**: Redux (for React) / LocalStorage

### Backend
- **Framework**: Flask / FastAPI (Python)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens
- **Validation**: Pydantic (FastAPI) / WTForms (Flask)

### Database
- **Development**: SQLite
- **Production**: MySQL / PostgreSQL
- **Caching**: Redis (optional)

### Optional AI Integration
- **NLP**: OpenAI API / Google Gemini
- **Use Cases**: 
  - Natural language timetable input
  - Study tips generation
  - Personalized recommendations

## 6. Security Considerations

- Password hashing (bcrypt/Argon2)
- JWT token authentication
- Input validation and sanitization
- SQL injection prevention (ORM)
- Rate limiting on API endpoints
- CORS configuration

## 7. Deployment Architecture

```
┌─────────────────────────────────────┐
│         Load Balancer (Nginx)       │
└─────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐         ┌─────────┐
│ App     │         │ App     │
│ Server  │         │ Server  │
│ (Flask) │         │ (Flask) │
└─────────┘         └─────────┘
    │                   │
    └─────────┬─────────┘
              ▼
    ┌─────────────────┐
    │    Database     │
    │  (MySQL/SQLite) │
    └─────────────────┘
```

## 8. Performance Optimization

- Database indexing on frequently queried columns
- Caching of computed schedules (Redis)
- Lazy loading for dashboard components
- Pagination for large datasets
- Background job processing for schedule generation

## 9. Monitoring & Logging

- Application logs (errors, warnings, info)
- Performance metrics (response times)
- User activity tracking
- Database query performance
- API endpoint usage statistics

## 10. Future Scalability

- Microservices architecture
- Container orchestration (Docker + Kubernetes)
- Cloud deployment (AWS/GCP/Azure)
- Mobile app development (React Native)
- Real-time notifications (WebSockets)
- Integration with calendar apps (Google Calendar)
