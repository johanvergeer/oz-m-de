#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace


rm -f './celerybeat.pid'
celery -A oz_m_de.taskapp beat -l INFO
