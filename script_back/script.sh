#!/bin/bash

build() {
    case $1 in
        k8s_front)
            echo "Building front-end..."
            # 프론트엔드 빌드 명령어 추가
            ;;
        k8s_back)
            echo "Building back-end..."
            # Python 소스 코드 컴파일 및 바이너리 생성 명령어
            pyinstaller --onefile backend/main.py --name backend_binary
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
    case $1 in
        k8s_front)
            echo "Creating front-end Docker image..."
            # 프론트엔드 도커 이미지 생성 명령어 추가
            ;;
        k8s_back)
            echo "Creating back-end Docker image..."
            docker build -t your_docker_repo/backend:latest .
            ;;
        k8s_all)
            make_image k8s_front
            make_image k8s_back
            ;;
        *)
            echo "Invalid image target"
            ;;
    esac
}

push_image() {
    case $1 in
        k8s_front)
            echo "Pushing front-end Docker image..."
            # 프론트엔드 도커 이미지 푸시 명령어 추가
            ;;
        k8s_back)
            echo "Pushing back-end Docker image..."
            docker push your_docker_repo/backend:latest
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
    make_image k8s_front
    push_image k8s_front
}

do_k8s_back_all() {
    build k8s_back
    make_image k8s_back
    push_image k8s_back
}

do_k8s_all() {
    do_k8s_front_all
    do_k8s_back_all
}

case $1 in
    build)
        build $2
        ;;
    make_image)
        make_image $2
        ;;
    push_image)
        push_image $2
        ;;
    do_k8s_front_all)
        do_k8s_front_all
        ;;
    do_k8s_back_all)
        do_k8s_back_all
        ;;
    do_k8s_all)
        do_k8s_all
        ;;
    *)
        echo "Invalid command"
        ;;
esac

