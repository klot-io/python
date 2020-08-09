FROM arm32v7/python:3.8.5-alpine3.12

RUN mkdir -p /opt/service

WORKDIR /opt/service

COPY requirements.txt .
COPY setup.py .
COPY lib lib

RUN apk add --no-cache --virtual .pip-deps  \
        gcc \
        libc-dev \
        make \
    && pip install --no-cache-dir -r requirements.txt \
	&& python setup.py install \
    && apk del --no-network .pip-deps \
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm requirements.txt \
	&& rm setup.py \
	&& rm -rf build \
	&& rm -rf dist \
	&& rm -rf lib/klotio_python.egg-info \
	&& rm -rf lib/klotio

ENV PYTHONPATH "/opt/service/lib:${PYTHONPATH}"
