# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = ccdb5_api
SOURCEDIR     = docsrc
BUILDDIR      = docs

MODULES := ccdb5_api complaint_search
GENDOCSRC := $(addsuffix .rst, $(MODULES))
GENDOCSRC := $(addprefix $(SOURCEDIR)/, $(GENDOCSRC))


all: clean-pyc test docs

test:
	coverage run manage.py test
	coverage html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-docs:
	rm -rf "$(BUILDDIR)"

docs: $(BUILDDIR)/index.html

regen-docs: clean-docs docs

$(BUILDDIR)/index.html: $(SOURCEDIR)/*.rst $(GENDOCSRC) $(SPHINXPROJ)/*.py
	@$(SPHINXBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

$(SOURCEDIR)/ccdb5_api.rst: $(SPHINXPROJ)/*.py
	rm -rf $@
	sphinx-apidoc -T -o "$(SOURCEDIR)" "$(SPHINXPROJ)"

$(SOURCEDIR)/complaint_search.rst: complaint_search/*.py
	rm -rf $@
	sphinx-apidoc -T -o  "$(SOURCEDIR)" complaint_search
