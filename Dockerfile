# Use a specific Python image
FROM python:3.10

# Create a non-privileged user for running the application
RUN useradd -m -s /bin/bash userapp

# Update and install necessary packages
RUN apt update \
    && apt install -y make \
    && apt install --no-install-recommends -y ca-certificates locales locales-all \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up locale settings
RUN locale-gen pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt_br
ENV LC_ALL pt_BR.UTF-8

# Remove log delay
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /home/userapp/app/src/

# Set the working directory
WORKDIR /home/userapp/app

# Copy only necessary files to install dependencies
COPY --chown=userapp:userapp ./pyproject.toml ./poetry.lock /home/userapp/app/

# Install Poetry and dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache -vvv

# Copy the rest of the application
COPY --chown=userapp:userapp . .

# Set the default user for running the application
USER userapp

# Set the entry point and default command
ENTRYPOINT ["poetry", "run", "--"]
CMD ["./start.sh"]
