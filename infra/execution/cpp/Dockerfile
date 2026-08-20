FROM gcc:13-bookworm

RUN groupadd --system runner \
    && useradd --system --gid runner --create-home --uid 10001 runner

WORKDIR /workspace

USER runner:runner

CMD ["/usr/bin/g++"]
