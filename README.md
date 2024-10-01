# Toolhunt API

This is a port of the [Toolhunt backend](https://github.com/wikimedia/toolhunt) to FastAPI.

Credit should be given to the original authors, mainly [nbarnabee](https://github.com/nbarnabee) as the principal contributor.

## Setting Up the Development Environment

To get the development environment up and running, follow these steps:

### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Poetry**: [Install Poetry](https://python-poetry.org/docs/#installation)

### Steps

1. **Clone the Repository**

   Clone the project repository to your local machine:

   ```sh
   git clone https://github.com/blancadesal/toolhunt-backend.git
   cd toolhunt-backend
   ```

2. **Install Python Dependencies**

   Use Poetry to install the Python dependencies:

   ```sh
   poetry install
   ```

3. **Build and Start Docker Containers**

   Build and start the Docker containers using Docker Compose:

   ```sh
   make start
   ```

   This will build the Docker images and start the containers defined in the `docker-compose.yml` file.

4. **Run the Database Migrations**

   Run the database migrations:

   ```sh
   make migrate
   ```

5. **Seed the Database**

   Seed the database with test data:

   ```sh
   make seed
   ```

6. **Run the Application**

   The application should now be running. You can access it at `http://localhost:8082`.

7. **Stopping the Containers**

   To stop the running containers:

   ```sh
   make stop
   ```

### Some Makefile Commands

- **`make start`**: Start the Docker containers.
- **`make stop`**: Stop the Docker containers.
- **`make restart`**: Restart the Docker containers.
- **`make status`**: Show the status of Docker containers.
- **`make web-logs`**: View logs from the web service.
- **`make init-db`**: Initialize the database schema.
- **`make migrations`**: Generate migration files.
- **`make migrate`**: Perform database migrations.
- **`make seed`**: Seed the database with test data.
- **`make db-shell`**: Access the database shell.

For a comprehensive list of commands, run `make`.
