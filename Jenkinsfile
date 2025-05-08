pipeline {
    agent { label 'KaliSlave136' }

    environment {
        IMAGE_NAME = 'appsec-demo'
        SCA_THRESHOLD = 3 // Breaks pipeline
        // SCA_THRESHOLD = 4
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
                    python3 -m venv app_venv
                    . app_venv/bin/activate
                    pip install -r app/requirements.txt
                '''
            }
        }

        /*
        stage('Static Application Security Testing (SAST) - Bandit') {
            steps {
                sh '''
                python3 -m venv bandit_venv
                . bandit_venv/bin/activate
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
                    python3 -m venv safety_venv
        
                    # Activate venv and install safety
                    . safety_venv/bin/activate
                    pip install safety
                    
                    pip uninstall -y urllib3
                    pip install urllib3
                    pip install --upgrade requests
                
                    # Run safety scan in JSON mode
                    safety check -r app/requirements.txt --json  > temp.json || true
                    
                    # Clear the safety warning
                    head -n -14 temp.json | tail -n +15 > safety-report.json
                    rm temp.json
                '''
                script {
                    def report = readJSON file: 'safety-report.json'
                    def remediations = report.remediations
                    
                    def hasTooManyVulns = remediations.any { pkgName, pkgData ->
                        pkgData.requirements.any { version, data ->
                            def vulnCount = data.vulnerabilities_found ?: 0
                               return vulnCount > $SCA_THRESHOLD 
                        }
                    }
                    
                    if (hasTooManyVulns) {
                        error("[!] SCA: One or more packages have more than 5 vulnerabilities. Failing the build.")
                    } else {
                        echo "[+] All packages passed the vulnerability threshold check."
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
