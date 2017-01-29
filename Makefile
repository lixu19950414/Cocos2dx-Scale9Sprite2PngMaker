.PHONY: run
run: code/compose.py
	python code/compose.py

.PHONY: clean
clean: dist build
	rm -rf dist build

.PHONY: buildWin
buildWin: code/compose.py code/setup.py
	python code/setup.py py2exe