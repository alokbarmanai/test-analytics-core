# Create a dictionary config mapping inside a new or existing helper module
# e.g., tests/config_factory.py

ENV_CONFIGS = {
    "testing": {
        "base_url": "http://127.0.0.1:8000",
        "db_connection": "sqlite:///./test_analytics.db",
        "timeout": 5,
    },
    "qa": {
        "base_url": "https://internal-analytics.com",
        "db_connection": "postgresql://qa_user:secure_pwd@qa-db:5432/analytics",
        "timeout": 10,
    },
    "production": {
        "base_url": "https://company.com",
        "db_connection": "postgresql://prod_user:hidden_pwd@prod-db:5432/analytics",
        "timeout": 30,
    },
}
