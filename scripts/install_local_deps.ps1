# Define dependencies
$dependencies = @("drunc", "druncschema")

# Define environment command
$env_cmd = ". /basedir/`${NIGHTLY_TAG}/env.sh"

# Install dependencies from local path
foreach ($dep in $dependencies) {
    $cmd = "pip install -e /mnt/local_deps/$dep"

    # Execute commands on different services
    docker compose exec --user root app bash -c "$cmd"
    docker compose exec --user root kafka_consumer bash -c "$cmd"
    docker compose exec drunc_pm bash -c "$env_cmd && $cmd"
    docker compose exec drunc_sm bash -c "$env_cmd && $cmd"
}
