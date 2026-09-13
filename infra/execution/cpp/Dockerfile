FROM gcc:13-bookworm

RUN groupadd --system --gid 1000 runner \
    && useradd --system --gid 1000 --create-home --uid 1000 runner

WORKDIR /workspace

USER runner:runner

CMD ["/usr/bin/g++"]
