%.png : %.dot
	dot -Tpng $< > $@

.PHONY: all

all: IND-CPA.png IND-EAV.png IND-CCA1.png IND-CCA2.png

.PHONY: dots
dots:
	python ttable2image.py





