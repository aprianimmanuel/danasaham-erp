# Start the Django development server
while true; do
    python manage.py runserver 0.0.0.0:8000

    # Check the exit status of the command
    if [ $? -eq 0 ]; then
        # If the command succeeds, break out of the loop
        break
    else
        # If the command fails, display an error message
        echo "Django server failed to start. Retrying..."
        sleep 0.5
    fi
done