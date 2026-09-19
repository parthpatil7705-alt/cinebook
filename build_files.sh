#!/bin/bash
echo "Installing dependencies..."
pip install --break-system-packages -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput
