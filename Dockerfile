FROM python:3.8-alpine as base

# Hard labels
LABEL maintainer="tech@cfpb.gov"

# Ensure that the environment uses UTF-8 encoding by default
ENV LANG en_US.UTF-8
ENV ENV /etc/profile
ENV PIP_NO_CACHE_DIR true
# Stops Python default buffering to stdout, improving logging to the console.
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /src/app
ENV ALLOWED_HOSTS '["*"]'

WORKDIR ${APP_HOME}

RUN apk update --no-cache && apk upgrade --no-cache && \
    pip install --upgrade pip setuptools

FROM base as builder

RUN apk add --no-cache --virtual .build-deps gcc git libffi-dev musl-dev postgresql-dev

COPY setup.py setup.py
RUN mkdir /build && pip install --prefix=/build .

FROM base as dev

RUN apk add --no-cahce --virtual .backend-deps curl postgresql

COPY --from=builder /build /usr/local
COPY setup.py setup.py
RUN pip install '.[testing]'

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base as final

COPY --from=builder /build /usr/local
RUN pip install gunicorn
RUN apk add --no-cache --virtual .deps postgresql-client

COPY . .

CMD ["gunicorn", "-c", "gunicorn.conf.py"]
