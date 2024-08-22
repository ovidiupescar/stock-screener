# Use an official Python runtime as a parent image
FROM python:3.12.5-slim

VOLUME [ "/scripts" ]

# Set the working directory in the container
WORKDIR /scripts

# Copy the current directory contents into the container at /app
COPY . /scripts

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "telegram_bot.py"]