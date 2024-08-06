FROM python:3.12.4-slim


# Install tzdata package to set timezone
RUN apt-get update && apt-get install -y tzdata

# Set the timezone to Mountain Time (change to your local)
ENV TZ=America/Denver

# Configure the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# Set the working directory to /app
WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron

# Create venv
RUN python3 -m venv venv

# Copy the requirements.txt file to the working directory
COPY requirements.txt /app

# Activate venv_app
RUN . venv/bin/activate && pip install -r requirements.txt

COPY ./scheduler /app/scheduler
COPY ./utils /app/utils
COPY ./cli /app/cli
COPY ./utils/.env /app/utils

# Add cron jobs - 1 for download and 1 for prediction
RUN echo "45 10 * * 2,3,4 /app/venv/bin/python /app/utils/main.py" > /etc/cron.d/mycron
RUN echo "55 10 * * 2,3,4 cd /app/cli && /app/venv/bin/python main.py" >> /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron

# Apply cron job
RUN crontab /etc/cron.d/mycron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

#CMD ["python", "/app/utils/main.py"]
#CMD ["ls -l /app/utils/" ]

