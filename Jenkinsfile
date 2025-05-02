pipeline {
    agent { label 'KaliSlave131' }

    environment {
        IMAGE_NAME = 'appsec-demo'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/rbozburun/appsec-pipeline-demo.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r app/requirements.txt'
            }
        }

        stage('Static Application Security Testing (SAST) - Bandit') {
            steps {
                sh '''
                pip install bandit
                bandit -r app/ -f json -o bandit-result.json || true
                '''
                script {
                    def banditReport = readJSON file: 'bandit-result.json'
                    def hasHighIssues = banditReport.results.any { it.issue_severity == 'HIGH' }
                    if (hasHighIssues) {
                        error("Bandit: High level security vulnerability found!")
                    }
                }
            }
        }
       
        /*
        stage('SCA Scan - OWASP Dependency Check') {
            steps {
                sh '''
                curl -L -o dependency-check.zip https://github.com/jeremylong/DependencyCheck/releases/download/v8.4.0/dependency-check-8.4.0-release.zip
                unzip dependency-check.zip -d dependency-check
                ./dependency-check/bin/dependency-check.sh --project "AppSec Demo" --scan app/ --format "JSON" --out ./dependency-report
                '''
                script {
                    def report = readJSON file: 'dependency-report/dependency-check-report.json'
                    def hasCritical = report.dependencies.any { dep ->
                        dep.vulnerabilities?.any { it.severity == 'Critical' || it.cvssScore >= 7.0 }
                    }
                    if (hasCritical) {
                        error("SCA: Critical security vulnerability found!")
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d --build'
            }
        }

        stage('DAST Scan - OWASP ZAP') {
            steps {
                script {
                    sleep 10
                    sh '''
                    docker run --rm -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
                        -t http://host.docker.internal:5000 \
                        -r zap-report.html -J zap-report.json \
                        || true
                    '''
                    def zapReport = readJSON file: 'zap-report.json'
                    def hasHigh = zapReport.site.alerts.any { it.riskdesc.startsWith("High") || it.riskdesc.startsWith("Medium") }
                    if (hasHigh) {
                        error("ZAP: High/Medium level security vulnerability found!")
                    }
                }
            }
        }
    }
    */

    post {
        // Will be executed if the pipeline fails at any stage
        failure {
            script {
                echo "Pipeline failed! The code won't be deployed."
                sh 'docker-compose down || true' 
                }
            }
        }
    }

}
