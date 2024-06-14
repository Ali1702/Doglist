import os

class Config:
    KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'http://keycloak:8080/')
    KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME', 'MyRealm')
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'doglist-client')
    KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', 'itAQNaIs8E4JJosxxCU7mEpuYGe4Kx0V')