call venv\Scripts\activate
rm -rf dist build
python setup.py build
call deactivate
