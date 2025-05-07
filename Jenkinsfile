pipeline {
    agent { label 'KaliSlave136' }

    environment {
        IMAGE_NAME = 'appsec-demo'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/rbozburun/appsec-pipeline-demo']])
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r app/requirements.txt
                '''
            }
        }

        /*
        stage('Static Application Security Testing (SAST) - Bandit') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install bandit
                bandit -r app/ -f json -o bandit-result.json --exit-zero
                '''
                script {
                    echo "[+] SAST scan finished, analyzing results..."
                    def banditReport = readJSON file: 'bandit-result.json'
                    def totals = banditReport.metrics["_totals"]
                    def highIssueCount = totals['SEVERITY.HIGH']
                    def mediumIssueCount = totals['SEVERITY.MEDIUM']
                    
                    echo "[+] $totals"
                    if (highIssueCount > 0) {
                        error("[!] SAST: $highIssueCount high level issue(s) detected! Fix them before deployment.")
                    } 
                    if (mediumIssueCount > 0) {
                        error("[!] SAST: $mediumIssueCount medium level issue(s) detected! Fix them before deployment.")
                    }
                    
                    
                }
            }
        } 
        */
        
        
        stage('SCA Scan - Safety') {
            steps {
                sh '''
                    # Create virtual environment
                    python3 -m venv venv
        
                    # Activate venv and install safety
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install safety
        
                    # Run safety scan in JSON mode
                    safety check -r app/requirements.txt --json  > safety-report.json
                '''
                script {
                    def report = readJSON file: 'safety-report.json'
        
                    def hasCritical = report.any { vuln ->
                        def severity = (vuln.severity ?: 'low').toLowerCase()
                        return severity == 'critical' || severity == 'high'
                    }
        
                    if (hasCritical) {
                        error("SCA: Critical or high severity vulnerabilities found by Safety!")
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
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        }
        
        /*
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

    }

}
