#!/bin/bash

# Compose actions
_start_compose() {
    echo "Starting development environment..."
    docker compose up -d
}

_stop_compose() {
    echo "Stopping development environment..."
    docker compose down
}

_remove_compose() {
    echo "Removing development environment..."
    docker compose down -v
}

_logs_compose() {
    echo "Showing logs from all containers..."
    docker compose logs -f
}

_build_compose() {
    echo "Building development environment..."
    docker compose build
}

#Flask actions
_start_flask() {
    echo "Starting Flask server..."
    docker compose up -d flask
}

_stop_flask() {
    echo "Stopping Flask server..."
    docker compose down flask
}

_logs_flask() {
    echo "Showing logs from Flask container..."
    docker compose logs -f flask
}

_bash_flask() {
    echo "Starting bash in Flask container..."
    docker compose exec -it flask bash
}

_shell_flask() {
    echo "Starting shell in Flask container..."
    docker compose exec -it flask python -i models.py
}

# Database actions
_start_db() {
    echo "Starting database..."
    docker compose up -d db
}

_stop_db() {
    echo "Stopping database..."
    docker compose down db
}

_logs_db() {
    echo "Showing logs from database container..."
    docker compose logs -f db
}

_mysql_db() {
    echo "Starting MySQL client..."
    docker compose exec db mysql -u root -prootpassword
}

_upgrade_db() {
    echo "Upgrading database..."
    echo "Not implemented yet!!!"
}

# Usage
_usage() {
    echo "usage: fdev [compose | flask | db]"
    echo "Compose usage: fdev compose [start | stop | restart | remove | build | logs]"
    echo "Flask usage: fdev flask [start | stop | restart | logs | bash | shell]"
    echo "Database usage: fdev db [start | stop | restart | logs | mysql | upgrade]"
    echo for more information, see the README.md
}
