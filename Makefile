test:
	python setup.py test
pypi: test
	./mkchangelog
	python setup.py register sdist bdist_egg upload
