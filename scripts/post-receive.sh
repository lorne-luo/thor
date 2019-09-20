#!/bin/bash
while read oldrev newrev refname
do
    branch=$(git rev-parse --symbolic --abbrev-ref $refname)
    if [ "dev" == "$branch" ]; then
        sudo git --git-dir=/home/git/thor.git --work-tree=/opt/thor checkout -f dev >/dev/null
        cd /opt/thor

        PIP=/home/luotao/venv/thor/bin/pip
        PYTHON=/home/luotao/venv/thor/bin/python
        sudo ${PIP} install -r requirements.txt || exit 1
        sudo chown luotao /home/luotao/venv/thor -R

        sudo ${PYTHON} manage.py migrate
        # sudo ${PYTHON} manage.py js_reverse
        # sudo gulp build
        npm install
        npm run build-assets
        npm run build-emails

        sudo ${PYTHON} manage.py collectstatic --noinput

        sudo supervisorctl restart thor
    fi
done
