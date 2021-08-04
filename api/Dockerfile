FROM python:3.8-slim

# install python requirements
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --verbose -r /requirements.txt

# copy the actual API source code
COPY app.py /app/app.py
WORKDIR /app/

# ENV PYTHONPATH=/app
EXPOSE 5000

CMD ["gunicorn", \
  "--bind", "0.0.0.0:5000", \
  "--log-level", "info", \
  "--graceful-timeout", "90", \
  "--timeout", "90", \
  "--workers", "2", \
  "app:app" \
]
