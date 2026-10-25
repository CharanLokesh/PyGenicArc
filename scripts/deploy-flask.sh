
#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE_URI="${1:?Usage: deploy-flask.sh IMAGE_URI}"
CONTAINER="flask-starter-project"
PORT="5000"
REGION="ap-south-1"
LOG_GROUP="/flask-starter/production"
HEALTH_URL="http://127.0.0.1:${PORT}/health"

OLD_IMAGE=""
if docker inspect "$CONTAINER" >/dev/null 2>&1; then
    OLD_IMAGE=$(docker inspect --format '{{.Config.Image}}' "$CONTAINER")
fi

run_container() {
    local image="$1"

    docker run -d \
        --name "$CONTAINER" \
        --restart unless-stopped \
        --log-driver awslogs \
        --log-opt "awslogs-region=${REGION}" \
        --log-opt "awslogs-group=${LOG_GROUP}" \
        --log-opt "awslogs-stream=flask-app" \
        -p "${PORT}:5000" \
        "$image"
}

rollback() {
    echo "Deployment failed; attempting rollback."
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

    if [[ -n "$OLD_IMAGE" ]]; then
        docker image inspect "$OLD_IMAGE" >/dev/null 2>&1 || docker pull "$OLD_IMAGE"
        run_container "$OLD_IMAGE"
        echo "Rollback container started with ${OLD_IMAGE}"
    else
        echo "No previous image available for rollback."
    fi
}

docker pull "$IMAGE_URI"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

if ! run_container "$IMAGE_URI"; then
    rollback
    exit 1
fi

for attempt in $(seq 1 20); do
    if curl --fail --silent --max-time 5 "$HEALTH_URL" >/dev/null; then
        echo "Deployment successful: $IMAGE_URI"
        exit 0
    fi
    sleep 3
done

docker logs "$CONTAINER" || true
rollback
exit 1
