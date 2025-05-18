pipeline {
    agent any
    environment {
        VENV_DIR = 'venv'
        PYTHON = "${env.WORKSPACE}/${VENV_DIR}/bin/python"
        PIP = "${env.WORKSPACE}/${VENV_DIR}/bin/pip"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Set up Python venv') {
            steps {
                sh '''
                python3 -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                ${PIP} install --upgrade pip
                ${PIP} install -r requirements.txt
                '''
            }
        }
        stage('Lint') {
            steps {
                sh '''
                . ${VENV_DIR}/bin/activate
                ${PIP} install flake8
                ${VENV_DIR}/bin/flake8 api/ src/ main.py || true
                '''
            }
        }
        stage('Run pipeline') {
            steps {
                sh '''
                . ${VENV_DIR}/bin/activate
                ${PYTHON} main.py --pois_dir data/POIs --streets_dir data/STREETS_NAMING_ADDRESSING --output_dir output --test_mode
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'output/**/*', fingerprint: true
            archiveArtifacts artifacts: 'logs/**/*', fingerprint: true
        }
        failure {
            mail to: 'tu-email@dominio.com',
                 subject: "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Check Jenkins for details."
        }
    }
}
