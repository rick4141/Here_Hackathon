pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        PYTHON = "${WORKSPACE}/${VENV_DIR}/bin/python3"
        PIP = "${WORKSPACE}/${VENV_DIR}/bin/pip3"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/rick4141/Here_Hackathon.git'
            }
        }
        stage('Set up Python virtual environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    ${PIP} install --upgrade pip
                '''
            }
        }
        stage('Install Requirements') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    ${PIP} install -r requirements.txt
                '''
            }
        }
        stage('Run Pipeline in Test Mode') {
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
            archiveArtifacts artifacts: '**/*.log,**/output/**', allowEmptyArchive: true
        }
        failure {
            echo 'Build failed!'
        }
        success {
            echo 'Build succeeded!'
        }
    }
}
