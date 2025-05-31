#! /bin/bash
pytest test -v --disable-warnings --junitxml=/reports/backend-test-results.xml
chmod o+rwx /reports/backend-test-results.xml
