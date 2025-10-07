FROM python:3.10-slim

WORKDIR /app

# copy backend sources
COPY . /app

# install build deps and python deps
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
