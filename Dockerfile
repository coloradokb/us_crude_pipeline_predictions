FROM python:3.12-slim

ENV TZ=America/Denver
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV PATH=/app/venv/bin:$PATH

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docker-entrypoint.sh .

RUN chmod +x /app/docker-entrypoint.sh \
    && echo "45 8 * * 3,4 cd /app && /app/venv/bin/python -m pipeline_pred.cli run-pipeline >> /var/log/cron.log 2>&1" > /etc/cron.d/pipeline-pred \
    && chmod 0644 /etc/cron.d/pipeline-pred \
    && crontab /etc/cron.d/pipeline-pred \
    && touch /var/log/cron.log

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["api"]
