init:
	pip3 install .

test:
	pytests tests --html=documentation/build/html/test_output.html
