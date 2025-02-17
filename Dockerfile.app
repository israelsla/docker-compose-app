FROM python:3.9-slim-buster

WORKDIR /app

COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app/. .
RUN chmod +x entrypoint.sh

EXPOSE 5000

CMD ["./entrypoint.sh"]
