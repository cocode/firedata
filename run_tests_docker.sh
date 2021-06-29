set -euo PIPEFAIL
git pull
pytest
mypy .
coverage run -m pytest
coverage report -m