FROM python

RUN apt-get update
#RUN apt-get install -y make automake gcc g++ subversion python3-dev libffi-dev

WORKDIR /
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
RUN tar -xzf ta-lib-0.4.0-src.tar.gz
WORKDIR /ta-lib
RUN ./configure --prefix=/usr
RUN make
RUN make install

WORKDIR /app

COPY requirements.txt ./

RUN pip install numpy==1.19.0

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./