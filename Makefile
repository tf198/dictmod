
all: test help

help: docs/dictmod.md

docs/dictmod.md: dictmod/__init__.py
	pydoc dictmod > $@

test:
	python -m doctest dictmod/__init__.py