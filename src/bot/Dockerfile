FROM python:3.12.9-bookworm

RUN sed -i 's/^Components: main$/& contrib non-free/' /etc/apt/sources.list.d/debian.sources
WORKDIR /app

RUN apt-get update
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]