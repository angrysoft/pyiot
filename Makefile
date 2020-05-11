PREFIX = /usr
PYTHON = python3

all: doc build

doc: setup.py
	$(PYTHON) setup.py build_sphinx

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py -v install --prefix=$(PREFIX) --record files.txt

uninstall:
	./uninstall.py
