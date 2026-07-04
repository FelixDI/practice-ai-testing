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
        // 3. UI 测试（检测 Cloudflare）
        // ----------------------------------------------------------------
        stage('UI Tests') {
            when { expression { env.SKIP_TESTS != 'true' } }
            steps {
                script {
                    def blocked = sh(
                        script: '''
                            STATUS=$(curl -sI -o /dev/null -w "%{http_code}" https://practicesoftwaretesting.com/ --max-time 10)
                            BODY=$(curl -s https://practicesoftwaretesting.com/ --max-time 10 | head -5)
                            if echo "$BODY" | grep -qiE "cloudflare|checking your browser|403.*denied"; then
                                echo "blocked"
                            elif [ "$STATUS" != "200" ]; then
                                echo "blocked"
                            else
                                echo "ok"
                            fi
                        ''',
                        returnStdout: true
                    ).trim()

                    if (blocked == 'ok') {
                        sh '''
                            uv run playwright install chromium
                            uv run pytest tests/ui \
                                -v \
                                --tb=line \
                                --screenshot=only-on-failure \
                                --alluredir=allure-results-ui \
                                --junitxml=junit-ui.xml \
                                || true
                        '''
                        stash includes: 'allure-results-ui/**', name: 'ui-results'
                    } else {
                        echo '⚠️ 站点被 Cloudflare 拦截，跳过 UI 测试'
                    }
                }
            }
            post {
                always {
                    junit 'junit-ui.xml'
                    archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
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

                // 推送到 gh-pages
                withCredentials([string(credentialsId: 'github-token', variable: 'GH_TOKEN')]) {
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

    post {
        always {
            cleanWs()
        }
    }
}
