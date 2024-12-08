Here’s a `README.md` template you can use for your GitHub repository, which provides detailed instructions on how to set up and run the project using Docker and Docker Compose.

---

# BikeGo App

This project is a Flask-based application that connects to a PostgreSQL database and provides an API for managing bike-related data. It also includes PGAdmin for database management.

## Live Production Version

A production version of this application is available at:
👉 https://bikego.selecro.cz

## Prerequisites

- **Docker** and **Docker Compose** are required to run this project.

Make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/yourusername/bikego-app.git
cd bikego-app
```

### 2. Set Up the Environment

You’ll need to create a `.env` file in the root directory of the project. This file will store environment variables used by Docker Compose and the application.

Here’s a sample `.env` file:

```dotenv
FLASK_APP=app.py
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_SCHEMA=public
JWT_SECRET_KEY=your_secret_key
IMGUR_CLIENT_ID=your_client_id
IMGUR_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your_email
SENDER_PASSWORD=your_email_password
```

Replace the placeholder values with your own secrets and database credentials.

### 3. Build the Docker Images

Once your `.env` file is ready, you can build the Docker images and start the services with Docker Compose.

```bash
docker-compose build
```

This will build the required containers for the Flask application, PostgreSQL database, and PGAdmin.

### 4. Run the Application

After the build process completes, you can start the application and all services by running:

```bash
docker-compose up
```

This will start the following containers:

- `bikego_postgres`: PostgreSQL database container.
- `bikego_pgadmin4`: PGAdmin for database management.
- `bikego`: The Flask application running with Gunicorn.

### 5. Access the Application

- The Flask application will be accessible at [http://localhost:5000](http://localhost:5000).
- PGAdmin will be available at [http://localhost:5050](http://localhost:5050). The default login credentials are configured in your `.env` file:
  - **Email**: `your_email`
  - **Password**: `your_email_password`

### 6. Healthchecks

Each service in the `docker-compose.yml` file includes a health check to ensure they are running correctly:
- **PostgreSQL**: Uses `pg_isready` to check if the database is ready.
- **PGAdmin**: Checks if the web interface is responsive.
- **Flask App**: Performs an HTTP request to ensure the app is responding.

### 7. Stopping the Services

To stop the services, use the following command:

```bash
docker-compose down
```

This will stop and remove all the containers created by Docker Compose.

### 8. Restarting the Services

If you make changes to the code or environment variables, you can rebuild and restart the services:

```bash
docker-compose down
docker-compose build
docker-compose up
```

## Troubleshooting

### `gunicorn: executable file not found in $PATH`

This error occurs when the `gunicorn` executable isn't installed or accessible in the container. To fix it:

1. Ensure `gunicorn` is listed in `requirements.txt`.
2. Ensure your `Dockerfile` has the correct installation commands and environment variables.

### Logs

If you encounter issues, you can view the logs of any container with:

```bash
docker-compose logs <container_name>
```

For example, to check the logs for the Flask app container:

```bash
docker-compose logs bikego
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This `README.md` provides a comprehensive guide for setting up, running, and troubleshooting the project. Modify any sections as needed to fit the specifics of your application.Here’s a `README.md` template you can use for your GitHub repository, which provides detailed instructions on how to set up and run the project using Docker and Docker Compose.

---

# BikeGo App

This project is a Flask-based application that connects to a PostgreSQL database and provides an API for managing bike-related data. It also includes PGAdmin for database management.

## Prerequisites

- **Docker** and **Docker Compose** are required to run this project.

Make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/yourusername/bikego-app.git
cd bikego-app
```

### 2. Set Up the Environment

You’ll need to create a `.env` file in the root directory of the project. This file will store environment variables used by Docker Compose and the application.

Here’s a sample `.env` file:

```dotenv
FLASK_APP=app.py
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_SCHEMA=public
JWT_SECRET_KEY=your_secret_key
IMGUR_CLIENT_ID=your_client_id
IMGUR_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your_email
SENDER_PASSWORD=your_email_password
```

Replace the placeholder values with your own secrets and database credentials.

### 3. Build the Docker Images

Once your `.env` file is ready, you can build the Docker images and start the services with Docker Compose.

```bash
docker-compose build
```

This will build the required containers for the Flask application, PostgreSQL database, and PGAdmin.

### 4. Run the Application

After the build process completes, you can start the application and all services by running:

```bash
docker-compose up
```

This will start the following containers:

- `bikego_postgres`: PostgreSQL database container.
- `bikego_pgadmin4`: PGAdmin for database management.
- `bikego`: The Flask application running with Gunicorn.

### 5. Access the Application

- The Flask application will be accessible at [http://localhost:5000](http://localhost:5000).
- PGAdmin will be available at [http://localhost:5050](http://localhost:5050). The default login credentials are configured in your `.env` file:
  - **Email**: `your_email`
  - **Password**: `your_email_password`

### 6. Healthchecks

Each service in the `docker-compose.yml` file includes a health check to ensure they are running correctly:
- **PostgreSQL**: Uses `pg_isready` to check if the database is ready.
- **PGAdmin**: Checks if the web interface is responsive.
- **Flask App**: Performs an HTTP request to ensure the app is responding.

### 7. Stopping the Services

To stop the services, use the following command:

```bash
docker-compose down
```

This will stop and remove all the containers created by Docker Compose.

### 8. Restarting the Services

If you make changes to the code or environment variables, you can rebuild and restart the services:

```bash
docker-compose down
docker-compose build
docker-compose up
```

## Troubleshooting

### `gunicorn: executable file not found in $PATH`

This error occurs when the `gunicorn` executable isn't installed or accessible in the container. To fix it:

1. Ensure `gunicorn` is listed in `requirements.txt`.
2. Ensure your `Dockerfile` has the correct installation commands and environment variables.

### Logs

If you encounter issues, you can view the logs of any container with:

```bash
docker-compose logs <container_name>
```

For example, to check the logs for the Flask app container:

```bash
docker-compose logs bikego
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---