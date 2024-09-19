# CSV Processing API

This Django-based REST API provides functionality for uploading and processing CSV files using Celery for asynchronous task handling.

## Features

- CSV file upload
- Asynchronous processing of CSV files
- Operations supported:
  - Deduplication
  - Unique value extraction
  - Filtering (Optional)

## Prerequisites

- Python 3.8+
- Redis (for Celery)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sameer2002ms/CSV_Backend_API.git
   cd csv_api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

## Running the Application

1. Start Redis server (ensure it's installed and running)

2. Start Celery worker:
   ```
   celery -A csv_api worker -l info -P gevent
   ```

3. Run the Django development server:
   ```
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`.
