pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Verify') {
            steps {
                sh 'make verify'
            }
        }
        stage('Push') {
            when {
                branch 'master'
            }
            steps {
                sh 'make push'
            }
        }
    }
}
