# FROM python:3.9

# WORKDIR /code

# COPY ./requirements.txt /code/requirements.txt
# COPY ./static/ /code/app/static/
# COPY ./templates/ /code/app/templates/
# COPY .env /code/app/.env
# COPY ./credentials.json /code/app/credentials.json

# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY ./app /code/app
# RUN ls -laR /code

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# # If running behind a proxy like Nginx or Traefik add --proxy-headers
# # CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]

FROM python:alpine

WORKDIR /

COPY ./requirements.txt /requirements.txt
COPY ./static/ /app/static/
COPY ./templates/ /app/templates/
COPY .env /app/.env
COPY ./credentials.json /app/credentials.json

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app/ /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]

