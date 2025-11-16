@echo off
echo Setting up Zistino Backend API...

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file from example
echo Creating .env file...
if not exist .env (
    copy env_example.txt .env
    echo Created .env file from template. Please update the values.
)

REM Run migrations
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo Creating superuser...
python manage.py createsuperuser

echo Setup complete!
echo To start the development server, run: python manage.py runserver
pause
