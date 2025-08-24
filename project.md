# Overview

A comprehensive Flask-based Task Manager web application that combines productivity features with gamification elements. The application allows users to create, manage, and track tasks while earning points and badges for completing them. It includes user authentication, task filtering/sorting, analytics dashboard, and responsive design.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Core web framework with modular structure
  - `app.py`: Application factory with database configuration
  - `main.py`: Application entry point
  - `routes.py`: Route handlers and business logic
  - `models.py`: SQLAlchemy ORM models
  - `utils.py`: Helper functions for analytics and data processing

## Database Design
- **SQLAlchemy ORM**: Database abstraction layer with PostgreSQL backend
- **User Model**: Stores user credentials (hashed passwords), points, and badge information
- **Task Model**: Manages task data including title, description, status, priority, due dates, and points
- **Relationship**: One-to-many between Users and Tasks with cascade delete

## Authentication & Security
- **Session-based authentication**: User sessions stored in Flask sessions
- **Password hashing**: Werkzeug's secure password hashing and verification
- **User isolation**: Each user can only access their own tasks through database queries filtered by user_id

## Frontend Architecture
- **Template Engine**: Jinja2 templating with template inheritance
- **Base Template**: Common layout with navigation, Bootstrap integration, and theme support
- **Responsive Design**: Bootstrap 5 framework with custom CSS enhancements
- **Dark Mode**: CSS custom properties with localStorage persistence
- **Icons**: Bootstrap Icons for consistent visual elements

## Gamification System
- **Points System**: Users earn points for completing tasks (configurable per task)
- **Badge System**: Three-tier badge system (Bronze/Silver/Gold) based on total points
- **Progress Tracking**: Visual representation of user achievements

## Analytics & Reporting
- **Dashboard**: Comprehensive analytics page with multiple metrics
- **Chart Integration**: Chart.js for data visualization
- **Analytics Functions**: Utility functions calculating task completion rates, priority distributions, and productivity trends

## Task Management Features
- **CRUD Operations**: Full create, read, update, delete functionality for tasks
- **Status Management**: Pending/Completed status with completion date tracking
- **Priority System**: High/Medium/Low priority levels with custom sorting
- **Date Management**: Due date tracking with overdue task identification
- **Filtering & Sorting**: Multiple filter options (all, pending, completed, overdue, upcoming) and sorting criteria

# External Dependencies

## Backend Dependencies
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: ORM integration for database operations
- **Werkzeug**: WSGI utilities and security features
- **SQLAlchemy**: Database toolkit and ORM

## Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework for responsive design and components
- **Bootstrap Icons 1.10.0**: Icon library for UI elements
- **Chart.js**: JavaScript library for data visualization and charts

## Database
- **PostgreSQL**: Primary database backend configured via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

## Development Environment
- **Environment Variables**: SESSION_SECRET for Flask sessions, DATABASE_URL for database connection
- **Logging**: Python logging for debugging and monitoring
- **Development Server**: Flask development server with hot reload