FROM python:3.13.0a3-alpine3.19

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /home/app/

COPY . /home/app

WORKDIR /home/app

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev

RUN python3 -m pip install --upgrade pip

EXPOSE 8000

RUN pip install -r requirements.txt

CMD ["python3","manage.py","runserver","0.0.0.0"]
