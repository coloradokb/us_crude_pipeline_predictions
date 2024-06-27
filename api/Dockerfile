FROM python:3.11-slim

#WORKDIR /utils


# Keep db conn pattenr fro ../utils
#RUN mkdir /utils
# WORKDIR /utils

# Set the working directory to /app
WORKDIR /app

# Create venv
RUN python3 -m venv venv

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Activate venv_app
RUN . venv/bin/activate && pip install -r requirements.txt

COPY requirements.txt .
COPY main.py .
COPY prediction_data.py .
COPY db_conn.py .
COPY .env .

# COPY pipeline_predictions.db .

COPY entrypoint.sh /
# RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Install NFS client package
# RUN apt-get update && \
#    apt-get install -y nfs-common && \
#    rm -rf /var/lib/apt/lists/*

# Create a directory to mount the NFS share
# RUN mkdir -p /datastore/pipeline/db
# Add entry point script

# Set entry point
# ENTRYPOINT ["/entrypoint.sh"]

#CMD ["python", "-u", "main.py"]
CMD ["sh", "-c", "(cd /app && . venv/bin/activate && python main.py)"]
