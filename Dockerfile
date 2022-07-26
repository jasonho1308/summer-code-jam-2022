FROM python:3.8-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./dev-requirements.txt /code/dev-requirements.txt
# Add C compiler
RUN apk add build-base
RUN pip install --no-cache-dir --upgrade -r /code/dev-requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code/app