#!/usr/bin/env bash
mkdir dist
pipenv lock -r > requirements.txt
pipenv run pip install -r requirements.txt --no-deps -t dist
cd dist && zip -r ../lambda_package.zip . > ../lambda_package_contents.txt && cd ..
zip -r lambda_package.zip main.py >> ./lambda_package_contents.txt
rm -rf dist requirements.txt