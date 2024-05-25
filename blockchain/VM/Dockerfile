ARG PYTHON_VERSION=3.9

FROM alpine:latest as builder
ENV PYROOT=/venv
ENV PYTHONUSERBASE=$PYROOT
COPY Pipfile* ./

RUN apk update && apk add --no-cache bc cargo gcc libffi-dev musl-dev openssl-dev rust python${PYTHON_VERSION}-dev py3-pip \
  && pip3 install --no-cache-dir --no-compile pipenv && pipenv lock && PIP_USER=1 pipenv sync --system

FROM alpine:latest as default

RUN apk add --no-cache git python${PYTHON_VERSION}
COPY --from=builder /venv /venv

ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/venv/lib/python${PYTHON_VERSION}/site-packages/"

WORKDIR /src
RUN pip3 install --no-cache-dir --no-compile -r /contract/requirements.txt
ENTRYPOINT ["python", "./smart_contract.py"]
