export AIRFLOW_HOME=~/airflow

AIRFLOW_VERSION=2.2.5

PYTHON_VERSION=3.8

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

airflow standalone