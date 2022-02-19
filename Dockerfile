FROM python:latest AS build
WORKDIR /app

COPY ./requirements.in ./

RUN python -m venv /venv \
    && /venv/bin/pip install -r requirements.in

FROM python:slim AS release
WORKDIR /app

EXPOSE 80
CMD ["/venv/bin/uvicorn", "backend.endpoints:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]

COPY --from=build /venv /venv
COPY . .
