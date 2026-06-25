NAME = inception
SRCS = ./srcs/docker-compose.yml

all: up

up:
	@mkdir -p /home/ylau-sim/data/wordpress
	@mkdir -p /home/ylau-sim/data/mariadb
	docker compose -f $(SRCS) up --build -d

down:
	docker compose -f $(SRCS) down

clean: down
	docker system prune -a

fclean: clean
	@sudo rm -rf /home/ylau-sim/data
	@if [ -n "$$(docker volume ls -q)" ]; then docker volume rm $$(docker volume ls -q); fi

re: fclean all

.PHONY: all up down clean fclean re
