FROM python:3.10

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . src
WORKDIR /src

EXPOSE 8000

# runs the production server
ENTRYPOINT ["python", "evms/manage.py"]
CMD ["runserver", "0.0.0.0:8000"]