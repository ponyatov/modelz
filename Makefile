MODULE = $(notdir $(CURDIR))

$(MODULE).py.log: $(MODULE).py $(MODULE).py.src
	python $^ && tail $(TAIL) $@
