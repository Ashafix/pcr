#!/usr/bin/env bash
cp html/primer.html /var/www/html/primer.html
cp cgi_bin/*  /var/www/cgi-bin/
cp data/batchprimer.conf /var/www/cgi-bin/
chown -R www-data:www-data /var/www
chown -R www-data:www-data /var/www/data

