#!/usr/bin/bash

dependencies="drunc druncschema"
env_cmd=". /basedir/\${NIGHTLY_TAG}/env.sh"

# Install <dependency> from ${DRUNC_LOCAL_DEPS}/<dependency>.
for dep in ${dependencies}
do
    cmd="pip install -e /mnt/local_deps/${dep}"
    docker compose exec --user root app bash -c "${cmd}"
    docker compose exec --user root kafka_consumer bash -c "${cmd}"
    docker compose exec drunc bash -c "${env_cmd} && ${cmd}"
done
