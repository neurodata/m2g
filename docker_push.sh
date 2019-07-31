#!/bin/bash
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker exec travis rm -r /input/*
docker exec travis rm -r /output/*
docker exec -w /ndmg travis git checkout staging
docker exec -w /ndmg travis git merge --no-edit $BRANCH
docker exec -w /ndmg travis git branch -D $BRANCH
docker commit -c 'ENTRYPOINT ["ndmg_bids"]' travis neurodata/ndmg_dev:latest
docker push neurodata/ndmg_dev:latest