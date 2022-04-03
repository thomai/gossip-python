FROM python:3.9-slim

ARG extra_os_packages
ARG optional_deps="[doc]"

# Initial setup for the container
RUN apt-get update
RUN apt-get install make man-db ${extra_os_packages} -y
RUN python3 -m pip install --upgrade pip

# Add source code
ADD . /app
WORKDIR /app

# Install package, use -e so you can mount project source via volume mount
# and dev without having to rebuild the container or reinstall the package.
RUN pip3 install .${optional_deps}

# Try building the documentation. If the user specifies optional dependencies
# that do not require doc then bail on this attempt (thus the `|| true` at the
# end).
RUN cd /app/documentation && make man && \
    mkdir /usr/local/man/man1 -p && \
    cp /app/documentation/build/man/gossip-python.1 /usr/local/man/man1/ && \
    gzip /usr/local/man/man1/gossip-python.1 && \
    mandb || true

CMD gossip
