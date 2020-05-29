
all: test help

help: docs/dictmod.txt

docs/dictmod.txt: dictmod/__init__.py
	pydoc dictmod > $@

test:
	python -m doctest dictmod/__init__.py