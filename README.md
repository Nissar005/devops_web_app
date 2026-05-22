# DevOps Web App

This repository contains a Django-based DevOps training platform with course catalog, learning modules, user accounts, and media support.

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `accounts/` — user registration and authentication
- `catalog/` — course management and content seeding
- `learning/` — lesson playback and student interface
- `course_platform/` — project settings and URLs

## Notes

- `media/course_videos/` is excluded from git.
- The repo initially pushed to `https://github.com/Nissar005/devops_web_app.git`.
