git clone https://github.com/cocode/firedata.git
cd /firedata
pytest
mypy .
coverage run -m pytest
