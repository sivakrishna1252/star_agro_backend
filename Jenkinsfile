pipeline {
    agent any

    environment {
        APP_NAME          = 'star-agro'
        APP_PORT          = '6021'
        DOCKER_REGISTRY   = "${env.DOCKER_REGISTRY ?: ''}"
        IMAGE_TAG         = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.take(7) ?: 'local'}"
        DOCKER_IMAGE      = "${DOCKER_REGISTRY ? DOCKER_REGISTRY + '/' : ''}${APP_NAME}:${IMAGE_TAG}"
        DOCKER_IMAGE_LATEST = "${DOCKER_REGISTRY ? DOCKER_REGISTRY + '/' : ''}${APP_NAME}:latest"
        COMPOSE_PROJECT   = "${env.COMPOSE_PROJECT_NAME ?: 'staragro'}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '5'))
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        booleanParam(
            name: 'SKIP_DEPLOY',
            defaultValue: false,
            description: 'Build and push only; skip docker compose deploy'
        )
        booleanParam(
            name: 'FORCE_DEPLOY',
            defaultValue: false,
            description: 'Deploy even on non-main branches'
        )
        choice(
            name: 'DEPLOY_TARGET',
            choices: ['local', 'ssh'],
            description: 'Deploy on Jenkins node (local) or remote server via SSH'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_BRANCH_NAME = env.BRANCH_NAME ?: env.GIT_BRANCH?.replace('origin/', '') ?: 'unknown'
                    env.GIT_SHORT_SHA = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Branch: ${env.GIT_BRANCH_NAME} | Commit: ${env.GIT_SHORT_SHA}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -eu
                    echo "Building ${DOCKER_IMAGE}"
                    docker build \
                        --pull \
                        --tag "${DOCKER_IMAGE}" \
                        --tag "${DOCKER_IMAGE_LATEST}" \
                        --label "org.opencontainers.image.revision=${GIT_COMMIT}" \
                        --label "org.opencontainers.image.source=${GIT_URL}" \
                        .
                    docker image inspect "${DOCKER_IMAGE}" >/dev/null
                '''
            }
        }

        stage('Django System Check') {
            steps {
                sh '''
                    set -eu
                    docker run --rm \
                        --entrypoint python \
                        -e SECRET_KEY=ci-check-only-not-for-production \
                        -e DEBUG=False \
                        -e ALLOWED_HOSTS=localhost \
                        -e DB_HOST=localhost \
                        -e DB_NAME=ci \
                        -e DB_USER=ci \
                        -e DB_PASSWORD=ci \
                        "${DOCKER_IMAGE}" \
                        manage.py check
                '''
            }
        }

        stage('Push to Registry') {
            when {
                expression {
                    return env.DOCKER_REGISTRY?.trim()
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${env.DOCKER_CREDENTIALS_ID ?: 'staragro-docker'}",
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    sh '''
                        set -eu
                        echo "${REGISTRY_PASS}" | docker login "${DOCKER_REGISTRY}" -u "${REGISTRY_USER}" --password-stdin
                        docker push "${DOCKER_IMAGE}"
                        docker push "${DOCKER_IMAGE_LATEST}"
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                expression {
                    def branch = env.GIT_BRANCH_NAME ?: ''
                    def isMain = branch in ['main', 'master']
                    return !params.SKIP_DEPLOY && (params.FORCE_DEPLOY || isMain)
                }
            }
            steps {
                script {
                    if (params.DEPLOY_TARGET == 'ssh') {
                        deployViaSsh()
                    } else {
                        deployLocal()
                    }
                }
            }
        }

        stage('Health Check') {
            when {
                expression {
                    def branch = env.GIT_BRANCH_NAME ?: ''
                    def isMain = branch in ['main', 'master']
                    return !params.SKIP_DEPLOY && (params.FORCE_DEPLOY || isMain)
                }
            }
            steps {
                sh '''
                    set -eu
                    echo "Waiting for app on port ${APP_PORT}..."
                    for i in $(seq 1 30); do
                        if curl -fsS "http://127.0.0.1:${APP_PORT}/" >/dev/null 2>&1; then
                            echo "Health check passed."
                            curl -fsS "http://127.0.0.1:${APP_PORT}/"
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Health check failed: service did not respond on port ${APP_PORT}"
                    docker compose -p "${COMPOSE_PROJECT}" ps
                    docker compose -p "${COMPOSE_PROJECT}" logs --tail=80 web
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded. Image: ${env.DOCKER_IMAGE}"
        }
        failure {
            echo 'Pipeline failed. Review stage logs above.'
        }
        always {
            sh '''
                docker image prune -f >/dev/null 2>&1 || true
            '''
        }
    }
}

def deployLocal() {
    withCredentials([file(
        credentialsId: "${env.ENV_CREDENTIALS_ID ?: 'staragro-env'}",
        variable: 'ENV_FILE'
    )]) {
        sh '''
            set -eu
            cp "${ENV_FILE}" .env

            export DOCKER_IMAGE="${DOCKER_IMAGE}"
            export APP_PORT="${APP_PORT}"
            export CREATE_SUPERUSER="${CREATE_SUPERUSER:-false}"
            export SEED_DATA="${SEED_DATA:-false}"

            docker compose -p "${COMPOSE_PROJECT}" down --remove-orphans || true
            docker compose -p "${COMPOSE_PROJECT}" up -d --no-build --pull missing
            docker compose -p "${COMPOSE_PROJECT}" ps
        '''
    }
}

def deployViaSsh() {
    withCredentials([
        file(
            credentialsId: "${env.ENV_CREDENTIALS_ID ?: 'staragro-env'}",
            variable: 'ENV_FILE'
        ),
        sshUserPrivateKey(
            credentialsId: "${env.SSH_CREDENTIALS_ID ?: 'staragro-ssh'}",
            keyFileVariable: 'SSH_KEY',
            usernameVariable: 'SSH_USER'
        )
    ]) {
        sh '''
            set -eu
            DEPLOY_HOST="${DEPLOY_HOST:?Set DEPLOY_HOST in Jenkins job environment}"
            DEPLOY_PATH="${DEPLOY_PATH:-/opt/star-agro}"

            ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no "${SSH_USER}@${DEPLOY_HOST}" \
                "mkdir -p '${DEPLOY_PATH}'"

            scp -i "${SSH_KEY}" -o StrictHostKeyChecking=no \
                docker-compose.yml Dockerfile \
                "${SSH_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/"

            scp -i "${SSH_KEY}" -o StrictHostKeyChecking=no \
                "${ENV_FILE}" \
                "${SSH_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/.env"

            ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no "${SSH_USER}@${DEPLOY_HOST}" \
                "cd '${DEPLOY_PATH}' && \
                 export DOCKER_IMAGE='${DOCKER_IMAGE}' APP_PORT='${APP_PORT}' CREATE_SUPERUSER=false SEED_DATA=false && \
                 docker compose -p '${COMPOSE_PROJECT}' pull web && \
                 docker compose -p '${COMPOSE_PROJECT}' up -d --no-build --remove-orphans && \
                 docker compose -p '${COMPOSE_PROJECT}' ps"
        '''
    }
}
