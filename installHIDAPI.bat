@echo off

ECHO building HIDAPI for iDDU

ECHO changing directory

cd .\cython_hidapi

ECHO generating Python code

python setup.py build

ECHO Installing ...

pip install -e .

ECHO SUCCESFULL!
