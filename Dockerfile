FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt ./

RUN pip installl --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD ["streamlit", "run", "src/main.py"]
