PYTHON_CMD = python
DOT_BUILDER = ttable2image.py
IMAGE_DIR = ../source/images

PNGS := IND-CPA.png IND-EAV.png IND-CCA1.png IND-CCA2.png
DOTS := $(PNGS:.png=.gv)
SVGS := $(PNGS:.png=.svg)

%.png : %.gv
	dot -Tpng $< > $@

%.svg : %.gv
	dot -Tsvg:cairo $< > $@

.PHONY: all

all: $(PNGS) $(SVGS)

.PHONY: export
export: $(PNGS) $(SVGS)
	cp $? $(IMAGE_DIR)

$(DOTS) : $(DOT_BUILDER)
	$(PYTHON_CMD) $(DOT_BUILDER)

.PHONY: clean
clean:
	rm -f $(PNGS) $(DOTS)






