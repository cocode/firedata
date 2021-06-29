set -euo pipefail
git pull
pytest
mypy .
coverage run -m pytest
coverage report -m