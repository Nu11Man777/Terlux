FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/terlux

RUN addgroup --system terlux && adduser --system --ingroup terlux terlux

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY terlux ./terlux
COPY wsgi.py ./

USER terlux
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=4s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3).status == 200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30", "--access-logfile", "-", "wsgi:app"]
