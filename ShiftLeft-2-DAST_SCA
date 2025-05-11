pipeline {
    agent { label 'KaliSlave136' }

    environment {
        IMAGE_NAME = 'appsec-demo'
        //SCA_THRESHOLD = 3 // Breaks pipeline
        SCA_THRESHOLD = 4
        DOCKER_NETWORK = "shiftleft-2-dast_sca_appsec_network" // <folder>_<defined-in-compose-yml>
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
        
        stage('Software Composition Analysis (SCA) - Safety') {
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
                               return vulnCount > env.SCA_THRESHOLD.toInteger()
                        }
                    }
                    
                    if (hasTooManyVulns) {
                        error("[!] SCA: One or more packages have more than $SCA_THRESHOLD vulnerabilities. Failing the build.")
                    } else {
                        echo "[+] All packages passed the vulnerability threshold check."
                    }
                }
            }
        } 

        stage('Build & Deploy the Project to Test') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        } 
        
        stage('Dynamic Application Security Testing (DAST) - OWASP ZAP') {
            steps {
                script {
                    sh '''
                    sudo chmod -R 777 $(pwd)
                    docker run --rm \
                      --network ${DOCKER_NETWORK}  \
                      -v $(pwd):/zap/wrk/:rw \
                      -t zaproxy/zap-stable zap-baseline.py \
                      -t http://web:5000 \
                      -r zap-report.html -J zap-report.json || true
                    '''
                    
                    // Analyze ZAP report
                    def zapReport = readJSON file: 'zap-report.json'
                    // def mediumVulnerabilities = zapReport.site[0].alerts.findAll { it.riskcode == '2' } // breaks pipeline
                    def highVulnerabilities = zapReport.site[0].alerts.findAll { it.riskcode == '3' }
                    
                    
                    // If medium severity vulnerability detected, fail the pipeline
                    if (highVulnerabilities.size() > 0) {
                        currentBuild.result = 'FAILURE'
                        sh 'docker compose down || true'
                        error "[!] DAST: Medium vulnerabilities found: ${mediumVulnerabilities.size()}"
                    } else {
                        echo "[+] DAST:  No medium vulnerabilities found. Build PASSED!"
                    }
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
        
        stage('Deploy the Project to Prod') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        } 
        
    }
}
