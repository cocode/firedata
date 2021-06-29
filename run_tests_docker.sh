set -euo pipefail
git pull
mypy .
coverage run -m pytest
coverage report -m