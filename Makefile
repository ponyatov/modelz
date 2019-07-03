MODULE = metaL
#$(notdir $(CURDIR))

$(MODULE).log: $(MODULE).py $(MODULE).ini
	python $^ > $@ && tail $(TAIL) $@
