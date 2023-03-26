FROM python:3.10

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

# ENV PYTHONPATH=/api

EXPOSE 8000

# ENTRYPOINT ["uvicorn"]
CMD [ "python", "main.py"]