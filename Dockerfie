FROM ubuntu:focal-20201106
RUN apt-get update -y && apt-get install -y python3-pip python-dev libpq-dev git curl
#RUN git clone https://github.com/fasten-project/LCV-CM.git
COPY . "/LCV-CM"
WORKDIR "/LCV-CM"
#RUN make
RUN pip3 install -r requirements.txt
#WORKDIR "/LCV-CM/src/LCV"
EXPOSE 3251
CMD ["python3","main.py"]