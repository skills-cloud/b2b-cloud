FROM python:3.9.5-buster as app
ENV \
    WORKDIR=/app \
    TERM=xterm \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1
WORKDIR $WORKDIR
RUN \
    apt-get update -y \
    && apt install -y \
        apt-utils \
        build-essential \
        ca-certificates \
        wget \
        curl \
        git \
        gnupg \
        gpg-agent \
        libboost-all-dev \
        libbz2-dev \
        libfreetype6-dev \
        libjpeg-dev \
        libjpeg62 \
        libpng-dev \
        libpq-dev  \
        libssl-dev \
        libtool \
        libwebp-dev \
        libwebp6
RUN pip install -U pip setuptools poetry
COPY poetry.lock pyproject.toml $WORKDIR/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
ADD . ${WORKDIR}
RUN ./manage.py collectstatic --noinput -v 0


FROM nginx:1.19.4-alpine as nginx
COPY --from=app /www/assets/ /www/assets/
