FROM ubuntu:jammy-20231128
RUN apt update && apt install -y python3-dev python3-pip nodejs npm libpq-dev git curl
RUN npm install -g newman
COPY . "/LCV-CM"
WORKDIR "/LCV-CM"
RUN pip3 install -r requirements.txt
EXPOSE 3251
RUN chmod +x entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]