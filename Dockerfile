FROM python:3.13-slim

ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt_br \
    LC_ALL=pt_BR.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/userapp/app/src/

RUN useradd -m -s /bin/bash userapp

# Install dependencies and clean up
RUN apt update && apt install -y --no-install-recommends \
        make \
        ca-certificates \
        locales \
        build-essential \
    && update-ca-certificates \
    && locale-gen pt_BR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/userapp/app

RUN python -m ensurepip --upgrade \
    && pip install --no-cache-dir --upgrade pip poetry \
    && poetry config virtualenvs.create false


COPY --chown=userapp:userapp pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-cache -vvv


COPY --chown=userapp:userapp . .


USER userapp

ENTRYPOINT ["poetry", "run", "--"]
CMD ["./start.sh"]
