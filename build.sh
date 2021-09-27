if [[ "$1" == "dev" ]]; then
    export COMPOSE_PROJECT_NAME=dochub-dev

    COMPOSE_FILE=docker/docker-compose.dev.yml
else
    export COMPOSE_PROJECT_NAME=dochub

    COMPOSE_FILE=docker/docker-compose.yml
fi

docker-compose -f $COMPOSE_FILE pull
docker-compose -f $COMPOSE_FILE up -d --build
docker-compose -f $COMPOSE_FILE exec web python manage.py migrate --noinput
docker-compose -f $COMPOSE_FILE exec web python manage.py collectstatic --no-input --clear
docker-compose -f $COMPOSE_FILE restart nginx  # Sometimes the connection between nginx and web fails
