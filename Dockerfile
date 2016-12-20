FROM python:3.4-alpine
ADD ./src /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 8000
CMD ["gunicorn", "app:app"]
