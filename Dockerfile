# Dockerfile for Django + PostgreSQL
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (if any)
RUN mkdir -p /app/static

# Expose port 8000 for Django
EXPOSE 8000

# Default command
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "research_data_app.wsgi:application", "--bind", "0.0.0.0:8000"]
