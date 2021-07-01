# Have to rebuild the docker image with --no-cache, if this file changes.
echo "+================================================"
echo Running run_tests_docker.sh
echo "-================================================"

set -euo pipefail
cat run_tests_docker.sh | sed "s/^/        /"
echo
echo "+================================================"
echo Running GIT PULL
echo "-================================================"
git pull
echo "+================================================"
echo Running MYPY
echo "-================================================"
mypy .
echo "+================================================"
echo Running COVERAGE
echo "-================================================"

coverage run -m pytest
echo "+================================================"
echo Running COVERAGE REPORT
echo "-================================================"
coverage report -m

echo "+================================================"
echo DONE run_tests_docker.sh
echo "-================================================"
