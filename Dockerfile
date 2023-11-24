# Use uma imagem Python específica
FROM python:3.10

# Cria um usuário não privilegiado para execução da aplicação
RUN useradd -m -s /bin/bash userapp

RUN apt update
RUN apt install make -y
RUN apt install --no-install-recommends -y \
    ca-certificates \
    locales locales-all \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt_br
ENV LC_ALL pt_BR.UTF-8

# Remove o delay do log
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /home/userapp/app/src/

# Define o diretório de trabalho
#WORKDIR /code

# Copia apenas os arquivos necessários para instalar as dependências
COPY --chown=userapp:userapp ./pyproject.toml ./
#COPY pyproject.toml /code/
# poetry.lock /app/

# Instala as dependências usando o Poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false


# Install Dependencies
RUN poetry install --no-interaction --no-cache -vvv

# Copia o restante da aplicação
COPY --chown=userapp:userapp . .
#/src /code/src

# Define o usuário padrão para execução da aplicação
USER userapp

ENTRYPOINT ["poetry", "run", "--"]
CMD ["./start.sh"]
# Configura o ponto de entrada e o comando padrão
#CMD ["poetry", "run", "uvicorn", "app:create_app()", "--host", "0.0.0.0", "--port", "8090"]
