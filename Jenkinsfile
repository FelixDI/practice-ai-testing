pipeline {
    agent any

    environment {
        PATH = "${HOME}/.local/bin:${PATH}"
    }

    stages {
        // ----------------------------------------------------------------
        // 0. 跳过纯文档变更
        // ----------------------------------------------------------------
        stage('Skip Docs-Only') {
            steps {
                script {
                    def hasCode = sh(
                        script: '''
                            FILES=$(git diff --name-only HEAD~1 2>/dev/null || git diff --name-only HEAD)
                            echo "$FILES" | grep -vE '\\.md$|\\.txt$|^\\.gitignore$|^docs/|^README'
                        ''',
                        returnStatus: true
                    )
                    if (hasCode != 0) {
                        echo '📄 仅文档变更，跳过测试'
                        env.SKIP_TESTS = 'true'
                    } else {
                        echo '🔧 代码变更，执行测试'
                        env.SKIP_TESTS = 'false'
                    }
                }
            }
        }

        // ----------------------------------------------------------------
        // 1. 环境准备
        // ----------------------------------------------------------------
        stage('Setup') {
            when { expression { env.SKIP_TESTS != 'true' } }
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    uv sync
                '''
                // 从 config.py 读取 Jenkins 专用账号，注入环境变量（凭据统一在 config.py 维护）
                script {
                    env.TEST_USER_EMAIL = sh(
                        script: '''uv run python -c "from src.common.config import JENKINS_TEST_EMAIL; print(JENKINS_TEST_EMAIL)"''',
                        returnStdout: true
                    ).trim()
                    env.TEST_USER_PASSWORD = sh(
                        script: '''uv run python -c "from src.common.config import JENKINS_TEST_PASSWORD; print(JENKINS_TEST_PASSWORD)"''',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        // ----------------------------------------------------------------
        // 2. API 测试
        // ----------------------------------------------------------------
        stage('API Tests') {
            when { expression { env.SKIP_TESTS != 'true' } }
            steps {
                sh '''
                    uv run pytest tests/api \
                        -v \
                        --tb=line \
                        --alluredir=allure-results-api \
                        --junitxml=junit-api.xml \
                        || true
                '''
            }
            post {
                always {
                    junit 'junit-api.xml'
                    stash includes: 'allure-results-api/**', name: 'api-results'
                }
            }
        }

        // ----------------------------------------------------------------
        // 3. UI 测试（Playwright 实测可达性，非 curl）
        // ----------------------------------------------------------------
        stage('UI Tests') {
            when { expression { env.SKIP_TESTS != 'true' } }
            steps {
                script {
                    // 安装 Chromium（检测和测试都需要）
                    sh 'uv run playwright install chromium'

                    // Playwright 实测：导航 + 等待 nav-home 渲染
                    def blocked = sh(
                        script: 'uv run python scripts/check_site_reachability.py',
                        returnStdout: true
                    ).trim()

                    // 脚本输出最后一行为判定结果，含 "blocked=true" 或 "blocked=false"
                    // 直接检查输出是否含 blocked=true
                    if (blocked.contains('blocked=true')) {
                        echo "⚠️ ${blocked}"
                    } else {
                        echo "✅ ${blocked}"
                        sh '''
                            uv run pytest tests/ui \
                                -v \
                                --tb=line \
                                --screenshot=only-on-failure \
                                --alluredir=allure-results-ui \
                                --junitxml=junit-ui.xml \
                                || true
                        '''
                        stash includes: 'allure-results-ui/**', name: 'ui-results'
                    }
                }
            }
            post {
                always {
                    junit 'junit-ui.xml'
                    archiveArtifacts(
                        artifacts: 'test-results/**, allure-results-ui/**, junit-ui.xml',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }

        // ----------------------------------------------------------------
        // 4. 生成 Allure 报告 → 推送到 gh-pages
        // ----------------------------------------------------------------
        stage('Deploy Allure Report') {
            when { expression { env.SKIP_TESTS != 'true' } }
            steps {
                script {
                    sh '''
                        # 安装 Allure CLI
                        ALLURE_VERSION=2.33.0
                        if [ ! -f "allure-${ALLURE_VERSION}.tgz" ]; then
                            curl -sLO https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz
                            tar -xzf allure-${ALLURE_VERSION}.tgz
                        fi

                        # 准备输出目录
                        rm -rf _site && mkdir -p _site

                        # 生成 API 报告
                        if [ -d "allure-results-api" ]; then
                            ./allure-${ALLURE_VERSION}/bin/allure generate \
                                allure-results-api \
                                -o _site/api-allure-report \
                                --clean
                        fi

                        # 生成 UI 报告
                        if [ -d "allure-results-ui" ]; then
                            ./allure-${ALLURE_VERSION}/bin/allure generate \
                                allure-results-ui \
                                -o _site/ui-allure-report \
                                --clean
                        fi
                    '''
                }

                // 推送到 gh-pages（含重试，GitHub Pages 偶发不可用）
                withCredentials([string(credentialsId: 'github-token', variable: 'GH_TOKEN')]) {
                    script {
                        def attempts = 0
                        retry(3) {
                            if (attempts > 0) {
                                sleep(time: 10, unit: 'SECONDS')
                            }
                            attempts++
                            sh '''
                                cd _site
                                git init
                                git config user.name  "Jenkins CI"
                                git config user.email "jenkins@ci.local"
                                git checkout -b gh-pages
                                git add .
                                git commit -m "Allure report [${BUILD_NUMBER}]" || true
                                git push -f "https://${GH_TOKEN}@github.com/FelixDI/practice-ai-testing.git" gh-pages
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
