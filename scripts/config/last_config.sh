#!/bin/bash
GENERIC_FOLDER=generic

echo "Qual sua versão do python? (3.10, 3.9, 3.6)"
read python_version

echo "Utilizando FastAPI? ([y]/n)"
read fastapi
if [[ -z $fastapi || $fastapi == "y" || $fastapi == "Y" ]]; then
    fastapi=true
fi

echo "Utilizando Django? ([y]/n)"
read django
if [[ $django == "y" || $django == "Y" || $django == "" ]]; then
    django=true
fi

echo -e "Deseja copiar o workflow de Deploy? (y/[n])\n\n===========\n** Cuidado para não sobrescrever os seus arquivos **\n===========\n"
read workflow_deploy
if [[ $workflow_deploy == "y" || $workflow_deploy == "Y" ]]; then
    workflow_deploy=true
fi

if [[ $workflow_deploy == true ]]; then
    echo "O deploy é feito no Kubernetes? ([y]/n)"
    read kubernetes
    if [[ $kubernetes == "y" || $kubernetes == "Y" || $kubernetes == "" ]]; then
        kubernetes=true
    fi

    if [[ ! $kubernetes == true ]]; then
        echo "O deploy é feito com serverless? ([y]/n)"
        read serverless
        if [[ $serverless == "y" || $serverless == "Y" || $serverless == "" ]]; then
            serverless=true
        fi
    fi
fi

echo "====================================================================="
echo "=========================== CONFIGURAÇÕES ==========================="
echo "====================================================================="
echo "python_version: $python_version"
echo "fastapi: $fastapi"
echo "django: $django"
echo "workflow_deploy: $workflow_deploy"
echo "kubernetes: $kubernetes"
echo "serverless: $serverless"
echo "====================================================================="
echo "===================== Deseja continuar? ([y]/n) ====================="
echo "====================================================================="
read continue
if [[ $continue == "y" || $continue == "Y" || $continue == "" ]]; then
    echo "Continuando..."
else
    echo "Saindo..."
    exit 1
fi

echo "Criando pasta temporária"
mkdir ./temp && cd ./temp

echo "Clonando o repositório de configurações"
git clone git@github.com:zapay-pagamentos/repo-config.git

if [[ $django == true ]]; then
    if [[ $fastapi == true ]]; then
        config_path="$python_version/FastAPI_Django"
    else
        config_path="$python_version/Django"
    fi
else
    config_path="$python_version/FastAPI"
fi

if [[ $workflow_deploy == true ]]; then
    if [[ $kubernetes == true ]]; then
        deploy_path="$GENERIC_FOLDER/workflows/kubernetes"
    fi

    if [[ $serverless == true ]]; then
        deploy_path="$python_version/workflows/serverless"
    fi
fi

################################################################################
# Arquivos de configuração
################################################################################
echo "Copiando .editorconfig"
cp ./repo-config/$GENERIC_FOLDER/.editorconfig ../

echo "Copiando .flake8"
cp ./repo-config/$GENERIC_FOLDER/.flake8 ../

echo "Copiando .pre-commit-config.yaml"
cp ./repo-config/$python_version/.pre-commit-config.yaml ../

echo "Copiando .pylintrc"
cp ./repo-config/$config_path/.pylintrc ../

echo "Copiando pr-titlec-checker-config.json"
cp ./repo-config/$GENERIC_FOLDER/workflows/pr-title-checker-config.json ../.github

################################################################################
# Scripts
################################################################################
echo "Copiando scripts do pre-commits"
if [ ! -d "../scripts" ]; then
    echo "Criando pasta scripts"
    mkdir ../scripts
fi

if [ ! -d "../scripts/pre-commit" ]; then
    echo "Criando pasta scripts/pre-commit"
    mkdir ../scripts/pre-commit
fi

echo "Copiando scripts/pre-commit/configure.sh"
cp ./repo-config/scripts/pre-commit/configure.sh ../scripts/pre-commit/

echo "Copiando scripts/pre-commit/run.sh"
cp ./repo-config/scripts/pre-commit/run.sh ../scripts/pre-commit/

echo "Copiando scripts/pre-commit/run_all.sh"
cp ./repo-config/scripts/pre-commit/run_all.sh ../scripts/pre-commit/
################################################################################
# Workflows
################################################################################
echo "Copiando os Workflows"

echo "Criando pasta .github caso não exista"
if [ ! -d "../.github" ]; then
    mkdir ../.github
fi
if [ ! -d "../.github/workflows" ]; then
    mkdir ../.github/workflows
fi

if [ ! -d "../.github/actions" ]; then
    mkdir ../.github/actions
fi

if [ ! -d "../.github/actions/action-repo-config" ]; then
    mkdir ../.github/actions/action-repo-config
fi

echo "Copiando action-repo-config.yml"
cp ./repo-config/$GENERIC_FOLDER/actions/action-repo-config.yml ../.github/actions/action-repo-config/action.yml

echo "Copiando check_pr_title.yml"
cp ./repo-config/$GENERIC_FOLDER/workflows/check_pr_title.yml ../.github/workflows/

echo "Copiando lint.yml"
cp ./repo-config/$config_path/workflows/lint.yml ../.github/workflows/

if [[ $workflow_deploy == true ]]; then
    echo "Copiando deploy.yml"
    cp ./repo-config/$deploy_path/deploy.yml ../.github/workflows/
fi

if [ ! -f "../.github/workflows/tests_and_sonar.yml" ]; then
    echo "Copiando tests_and_sonar.yml"
    cp ./repo-config/$python_version/workflows/tests_and_sonar.yml ../.github/workflows/
else
        cp ./repo-config/$python_version/workflows/tests_and_sonar.yml ../.github/workflows/new_tests_and_sonar.yml
        echo "********************************************************************************"
        echo "O arquivo tests_and_sonar.yml já existe, copiando para new_tests_and_sonar.yml"
        echo "Compare os dois arquivos e faça o merge manualmente"
        echo "********************************************************************************"
fi

echo "Limpando pasta temporária"
cd .. && rm -rf ./temp

echo "Configurações copiadas com sucesso!"
