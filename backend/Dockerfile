FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY startup.sh .

RUN chmod +x startup.sh

EXPOSE 8000

CMD ["./startup.sh"]
