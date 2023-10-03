FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /src
COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY src .
CMD python main.py
