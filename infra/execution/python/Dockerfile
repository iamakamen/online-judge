FROM python:3.12-alpine

RUN addgroup -S runner \
    && adduser -S -G runner -u 1000 runner

USER runner:runner

WORKDIR /workspace

CMD ["python3"]
