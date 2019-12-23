FROM python:3.8

WORKDIR /app

# .bashrc
COPY .bashrc /tmp/.bashrc
RUN cat /tmp/.bashrc >> /root/.bashrc

# Python requirements
COPY requirements.txt /app/
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1