#!/bin/bash

# 환경 변수 설정
PROJECT_NAME="kakao-sw-club"
ACC_KEY="005bb667e6574c61a5d4577262b61d89y"
SEC_KEY="652351ba4ebc7feec7e2e07582926c4ba7a06b09f2a1dbf4c223d15e15769a30761e63"
FRONT_IMAGE_NAME="frontend_image"
BACK_IMAGE_NAME="backend_image"
IMAGE_VERSION="1.0"\
REGISTRY_NAME="kakao-registry"
DOCKER_REGISTRY="${PROJECT_NAME}.kr-central-2.kcr.dev/${REGISTRY_NAME}"
REACT_APP_API_URL="your_api_url"

# Docker 로그인
docker_login() {
    echo "${SEC_KEY}" | sudo docker login ${PROJECT_NAME}.kr-central-2.kcr.dev --username ${ACC_KEY} --password-stdin
}

build() {
    case $1 in
        k8s_front)
            echo "Building front-end..."
            # 프론트엔드 빌드 명령어
            sudo docker build --build-arg REACT_APP_API_URL=${REACT_APP_API_URL} -t ${FRONT_IMAGE_NAME} -f Dockerfile.front .
            ;;
        k8s_back)
            echo "Building back-end..."
            # 백엔드 빌드 명령어
            sudo docker build -t ${BACK_IMAGE_NAME} -f Dockerfile.back .
            ;;
        k8s_all)
            build k8s_front
            build k8s_back
            ;;
        *)
            echo "Invalid build target"
            ;;
    esac
}

make_image() {
    echo "Docker 이미지 생성은 빌드 과정에서 수행됩니다."
}

push_image() {
    case $1 in
        k8s_front)
            echo "Pushing front-end Docker image..."
            sudo docker tag ${FRONT_IMAGE_NAME} ${DOCKER_REGISTRY}/${FRONT_IMAGE_NAME}:${IMAGE_VERSION}
            sudo docker push ${DOCKER_REGISTRY}/${FRONT_IMAGE_NAME}:${IMAGE_VERSION}
            ;;
        k8s_back)
            echo "Pushing back-end Docker image..."
            sudo docker tag ${BACK_IMAGE_NAME} ${DOCKER_REGISTRY}/${BACK_IMAGE_NAME}:${IMAGE_VERSION}
            sudo docker push ${DOCKER_REGISTRY}/${BACK_IMAGE_NAME}:${IMAGE_VERSION}
            ;;
        k8s_all)
            push_image k8s_front
            push_image k8s_back
            ;;
        *)
            echo "Invalid push target"
            ;;
    esac
}

do_k8s_front_all() {
    build k8s_front
    push_image k8s_front
}

do_k8s_back_all() {
    build k8s_back
    push_image k8s_back
}

do_k8s_all() {
    do_k8s_front_all
    do_k8s_back_all
}

case $1 in
    build)
        docker_login
        build $2
        ;;
    make_image)
        docker_login
        make_image $2
        ;;
    push_image)
        docker_login
        push_image $2
        ;;
    do_k8s_front_all)
        docker_login
        do_k8s_front_all
        ;;
    do_k8s_back_all)
        docker_login
        do_k8s_back_all
        ;;
    do_k8s_all)
        docker_login
        do_k8s_all
        ;;
    *)
        echo "Invalid command"
        ;;
esac
