FROM mxnet/python

LABEL MAINTAINER="abhin99"

RUN apt-get update

RUN pip3 uninstall mxnet -y

RUN pip3 install mxnet-mkl

ENV OMP_NUM_THREADS=2






