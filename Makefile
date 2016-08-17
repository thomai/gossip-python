init:
	pip install -r requirements.txt

test:
	py.test tests --html=documentation/_build/html/test_output.html

