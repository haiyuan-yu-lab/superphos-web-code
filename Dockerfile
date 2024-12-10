# Superphos
# Version: 1.0

FROM python:2.7

# Project Enviroment
RUN pip install pipenv
ENV VIRTUAL_ENV=/data/venv
RUN python -m virtualenv --python=/usr/bin/python $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Install Package Libraries
RUN pip install Flask==0.12.2 Flask-Bootstrap==3.3.7.1 Flask-Login==0.4.1 Flask-Migrate==2.3.1 Flask-SQLAlchemy==2.3.2 Flask-WTF==0.14.2
RUN pip install pandas numpy
RUN pip install alembic==1.0.5 boto==2.49.0 boto3==1.9.74 botocore==1.12.74 click==6.7 docutils==0.14 dominate==2.3.1 flask_table
RUN pip install futures==3.1.1 gunicorn==19.9.0 itsdangerous==0.24 Jinja2==2.10 jmespath==0.9.3
RUN Mako==1.0.7 MarkupSafe==1.0 
#pandas==0.24.2
RUN psycopg2==2.7.6.1
RUN Werkzeug==0.14.1 wheel==0.24.0 WTForms==2.2.1
RUN s3transfer==0.1.13 six==1.12.0 SQLAlchemy==1.2.15 urllib3==1.24.1 visitor==0.1.3

# Set the working directory in the container
WORKDIR /data/superphos
# Copy application files into the working directory
COPY . /data/superphos
# Project Files and Settings
VOLUME ["/data/superphos"]
# Set FLASK_APP environment variable
ENV FLASK_APP=main.py

# Server
EXPOSE 8967
STOPSIGNAL SIGINT
CMD ["flask", "run", "--host=0.0.0.0", "--port=8967"]