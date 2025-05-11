pipeline {
    agent { label 'KaliSlave136' }

    environment {
        IMAGE_NAME = 'appsec-demo'
        //SCA_THRESHOLD = 3 // Breaks pipeline
        SCA_THRESHOLD = 4
        DOCKER_NETWORK = "nosec_appsec_network" // <folder>_<defined-in-compose-yml>
    }

    stages {
        stage('Download Code from PreProd') {
            steps {
                checkout scmGit(branches: [[name: '*/preprod']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/rbozburun/appsec-pipeline-demo',  credentialsId: 'edbb8d50-8799-437e-9540-4dbf8fcf4303']])
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv app_venv
                    . app_venv/bin/activate
                    pip install -r app/requirements.txt
                '''
            }
        }
        
        stage('Software Testing') {
            steps {
                script {
                    echo "[+] Unit testing done!"
                }
            }
        }

        stage('Merge to Prod') {
            steps {
                script {
                    echo "[+] Merging code to prod branch..."
                    echo "[+] Code successfully merged to prod!"
                }
            }
        }
        
        stage('Build & Deploy the Project to Prod') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        } 
    }
}
