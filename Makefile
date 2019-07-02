MODULE = $(notdir $(CURDIR))

$(MODULE).log: $(MODULE).py $(MODULE).met
	python $^ > $@ && tail $(TAIL) $@
