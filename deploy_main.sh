#!/usr/bin/env bash
cp html/* /var/www/*
cp cgi_bin/*  /var/www/cgi-bin/
cp data/batchprimer.conf /var/www/cgi-bin/
chown -R www-data:www-data /var/www
chown -R www-data:www-data /var/www/data

