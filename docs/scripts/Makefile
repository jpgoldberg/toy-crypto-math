PYTHON_CMD = python
DOT_BUILDER = ttable2image.py
IMAGE_DIR = ../source/images

PNGS := IND-CPA.png IND-EAV.png IND-CCA1.png IND-CCA2.png
DOTS := $(PNGS:.png=.dot)

%.png : %.dot
	dot -Tpng $< > $@

.PHONY: all

all: $(PNGS)

.PHONY: export
export: $(PNGS)
	cp $(PNGS) $(IMAGE_DIR)

$(DOTS) : $(DOT_BUILDER)
	$(PYTHON_CMD) $(DOT_BUILDER)






