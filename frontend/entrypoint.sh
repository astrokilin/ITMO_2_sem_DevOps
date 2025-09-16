#!/bin/sh

if [ "$1" = "test" ]; then
  echo "Running frontend tests..."
  npm test -- --watchAll=false
  chmod o+rwx coverage/*
  chmod o+rwx coverage
  sed -i 's|app.jsx|frontend/app.jsx|g' coverage/cobertura-coverage.xml
  sed -i 's|<source>/app</source>|<source>frontend/app.jsx</source>|g' coverage/cobertura-coverage.xml
  sed -i.bak 's|SF:.*/frontend/|SF:frontend/|g' coverage/lcov.info
else
  echo "Starting frontend development server..."
  npm run dev -- --host 0.0.0.0
fi
