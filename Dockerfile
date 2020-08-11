FROM python:3
ENV PYTHONUNBUFFERED 1
USER 1000:1000
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
