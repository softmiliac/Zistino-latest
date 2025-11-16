#!/bin/bash
# Zistino Backend Setup Script

echo "Setting up Zistino Backend API..."

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file from example
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp env_example.txt .env
    echo "Created .env file from template. Please update the values."
fi

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

echo "Setup complete!"
echo "To start the development server, run: python manage.py runserver"
