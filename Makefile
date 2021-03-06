TARGET := sysid-ols.pdf

BIB := $(wildcard *.bib)
SVG := $(wildcard *.svg)
PDF_TEX := $(SVG:.svg=.pdf_tex)

.PHONY: all
all: $(TARGET)

$(TARGET): $(basename $(TARGET)).tex $(BIB)
	latexmk -interaction=nonstopmode -xelatex $(basename $@)

%.pdf_tex: %.svg
	inkscape -D -z --file=$< --export-pdf=$(basename $<).pdf --export-latex

.PHONY: format
format:
	./lint/format_bibliography.py
	./lint/format_json.py
	./lint/format_paragraph_breaks.py
	python3 -m black -q .

.PHONY: lint
lint: format
	./lint/check_filenames.py
	./lint/check_tex_includes.py
	./lint/check_tex_labels.py
	./lint/check_links.py
	git --no-pager diff --exit-code HEAD  # Ensure formatter made no changes

.PHONY: clean
clean: clean_tex
	rm -rf build

.PHONY: clean_tex
clean_tex:
	latexmk -xelatex -C
	rm -f sysid-ols.pdf

.PHONY: upload
upload:
	rsync --progress $(TARGET) file.tavsys.net:/srv/file/control/$(TARGET)

.PHONY: setup_arch
setup_arch:
	sudo pacman -Sy --needed --noconfirm \
		base-devel \
		biber \
		ghostscript \
		inkscape \
		texlive-bibtexextra \
		texlive-core \
		texlive-latexextra \
		python \
		python-black \
		python-pip \
		python-requests

.PHONY: setup_ubuntu
setup_ubuntu:
	sudo apt-get update -y
	sudo apt-get install -y \
		biber \
		build-essential \
		cm-super \
		ghostscript \
		inkscape \
		latexmk \
		texlive-bibtex-extra \
		texlive-latex-extra \
		texlive-xetex \
		python3 \
		python3-pip \
		python3-requests \
		python3-setuptools
	# The Ubuntu 20.04 package is too old
	pip3 install --user black
