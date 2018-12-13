#/bin/bash


export FLASK_APP=demo
export FLASK_ENV=development
# export FLASK_ENV=production

flask run -h 0.0.0.0 -p 11111
