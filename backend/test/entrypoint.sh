#! /bin/bash
pytest test -v --disable-warnings --junitxml=/reports/backend-test-results.xml --cov=app --cov-report=xml:/reports/coverage-backend.xml
chmod o+rwx /reports/backend-test-results.xml
chmod o+rwx /reports/coverage-backend.xml
chmod o+rwx /reports
# sed -i 's|app.py|./backend/app.py|g' /reports/coverage-backend.xml
sed -i 's|<source>/app</source>|<source>./backend</source>|g' /reports/coverage-backend.xml
