FROM ubuntu:focal-20201106
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python-dev libpq-dev git curl npm nodejs
RUN npm install -g newman
COPY . "/LCV-CM"
WORKDIR "/LCV-CM"
RUN pip3 install -r requirements.txt
EXPOSE 3251
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]