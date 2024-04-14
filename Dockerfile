FROM python:3.11

WORKDIR /code

COPY pyproject.toml poetry.lock /code/

RUN pip install poetry && poetry install --no-root

COPY ./app /code/api

CMD ["uvicorn", "--app-dir=.", "app.main:app", "--host", "0.0.0.0", "--port", "80"]