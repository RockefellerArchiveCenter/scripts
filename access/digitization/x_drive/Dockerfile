FROM python:3.12 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install Python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add application code
COPY process_packages.py .

ENTRYPOINT [ "python", "process_packages.py" ]