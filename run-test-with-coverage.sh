#!/bin/bash

"${VIRTUAL_ENV}/bin/coverage" run --source=taskstack taskstack/manage.py test taskstack
"${VIRTUAL_ENV}/bin/coverage" report -m taskstack/core/*.py
