FROM python

RUN apt-get update

WORKDIR /
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
RUN tar -xzf ta-lib-0.4.0-src.tar.gz
WORKDIR /ta-lib

RUN wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O ./config.guess
RUN wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O ./config.sub

RUN ./configure --prefix=/usr
RUN make
RUN make install

WORKDIR /app

COPY requirements.txt ./

RUN pip install numpy==1.19.0

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./