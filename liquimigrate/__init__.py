import os
LIQUIBASE_JAR = os.path.join(os.path.dirname(__file__), 'vendor',
    'liquibase.jar')
LIQUIBASE_DRIVERS = {
    'postgresql_psycopg2': ('postgresql', 'org.postgresql.Driver',
        os.path.join(os.path.dirname(__file__), 'vendor', 'connectors',
            'postgresql-jdbc3-8.2.jar')),
    'mysql': ('mysql', 'com.mysql.jdbc.Driver',
        os.path.join(os.path.dirname(__file__), 'vendor', 'connectors',
            'mysql-connector-java-5.0.8-bin.jar')),
}
