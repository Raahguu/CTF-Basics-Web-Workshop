FROM php:8.1-apache

RUN a2enmod rewrite headers

WORKDIR /var/www/html

COPY challenge/ .

COPY flag.txt /

RUN set -eux; \
    # Remove symlinks
    rm -f /var/log/apache2/access.log /var/log/apache2/error.log; \
    \
    # Create log files
    touch /var/log/apache2/access.log /var/log/apache2/error.log; \
    chown www-data:www-data /var/log/apache2/*.log; \
    chmod 644 /var/log/apache2/*.log

RUN echo "ServerName Brainfck101" >> /etc/apache2/apache2.conf

RUN chown -R www-data:www-data /var/www/html

CMD ["apache2-foreground"]
