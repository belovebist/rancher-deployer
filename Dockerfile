FROM python:alpine

# Use python3
ADD requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

ADD rancher.py /rancher/rancher.py
ADD rancher_cli /rancher/rancher_cli
ADD rancher/ /rancher/rancher

RUN chmod +x /rancher/rancher.py && \
    chmod +x /rancher/rancher_cli && \
    ln -s /rancher/rancher.py /bin/rancher && \
    ln -s /rancher/rancher_cli /bin/rancher_cli


# Add user to run the rancher deployer
RUN adduser -D -H rancher
USER rancher
