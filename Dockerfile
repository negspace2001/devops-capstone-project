FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
# Use option --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt
# Copy the service package or app contents
COPY service/ ./service/
# Create a non-root user theia and switch to it
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia
# Run the service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]