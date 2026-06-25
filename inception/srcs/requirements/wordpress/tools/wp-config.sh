#!/bin/sh

# 1. On se déplace là où WordPress doit être installé
cd /var/www/html

# 2. On récupère les mots de passe des secrets
WP_ADMIN_PASSWORD=$(cat /run/secrets/wp_admin_password)
WP_USER_PASSWORD=$(cat /run/secrets/wp_password)
MYSQL_PASSWORD=$(cat /run/secrets/db_password)

# 3. On attend que MariaDB soit prêt à accepter les connexions
sleep 10

# 4. On télécharge WordPress si ce n'est pas déjà fait
if [ ! -f "wp-config.php" ]; then
    wp core download --allow-root

    # 5. On crée le fichier wp-config.php
    wp config create --allow-root \
        --dbname="${MYSQL_DATABASE}" \
        --dbuser="${MYSQL_USER}" \
        --dbpass="${MYSQL_PASSWORD}" \
        --dbhost="mariadb:3306"

    # 6. On installe WordPress avec le domaine et les bons secrets
    wp core install --allow-root \
        --url="https://ylau-sim.42.fr" \
        --title="Inception" \
        --admin_user="${WP_ADMIN_USER}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL}"

    # 7. On crée le second utilisateur requis par le sujet
    wp user create "${WP_USER}" "${WP_USER_EMAIL}" \
        --user_pass="${WP_USER_PASSWORD}" \
        --role=author \
        --allow-root
fi

# 8. On lance PHP-FPM au premier plan
exec php-fpm7.4 -F
