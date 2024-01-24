FROM python:3.11

WORKDIR /grammar_pl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

WORKDIR /grammar_pl/grammar_pl
EXPOSE 8000