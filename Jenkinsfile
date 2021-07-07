pipeline {
  agent { docker { image 'python:3.8.10' } }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    stage('BookStore') {
      steps {
        sh 'python wsgi.py run'
      }
    }
  }
}