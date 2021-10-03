FROM python:3.9-slim-buster

WORKDIR /srv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install -y libpq-dev build-essential netcat git

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "incubator.wsgi:application", "--bind", "0.0.0.0:8000"]
