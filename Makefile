test:
	python setup.py test
pypi: test
	./mkchangelog
	python setup.py mregister sdist bdist_egg mupload
