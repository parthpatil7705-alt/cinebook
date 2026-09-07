#!/bin/bash
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Running migrations..."
python3 manage.py migrate --noinput
