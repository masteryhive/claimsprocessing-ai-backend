FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /home/ai_workflow
COPY ./pyproject.toml ./poetry.lock* ./

RUN pip install poetry
# Add --no-root to avoid installing the project itself during dependency installation
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache --no-root

EXPOSE 8080
CMD [ "python", "main.py" ]