#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


celery -A oz_m_de.taskapp worker -l INFO
