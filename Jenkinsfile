pipeline {
    agent node

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make build'
            }
        }
        stage('Setup') {
            steps {
                sh 'make setup'
            }
        }
        stage('Push') {
            steps {
                sh 'make push'
            }
        }
    }
}
