#!/bin/sh

apt update
apt install -y curl

while ! curl -s http://keycloak:8080; do
    echo "Waiting for Keycloak to be ready..."
    sleep 5
done

echo "Keycloak is ready."
flask run --host=0.0.0.0