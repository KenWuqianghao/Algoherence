FROM python:3.9-slim

WORKDIR /app

COPY . /app
# COPY ./graph /app/graph
# COPY ./table /app/table

RUN pip3 install -r requirements.txt

EXPOSE 8502

ENTRYPOINT ["streamlit", "run", "lit.py", "--server.port=8502", "--server.address=0.0.0.0"]