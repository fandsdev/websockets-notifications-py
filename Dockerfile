ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bookworm

ADD requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /src

ADD src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
