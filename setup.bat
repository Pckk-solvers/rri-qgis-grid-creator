@echo off
setlocal enabledelayedexpansion

echo ���z���̃Z�b�g�A�b�v���J�n���܂�...

:: Python�̃o�[�W�����m�F
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python���C���X�g�[������Ă��Ȃ����APATH�ɒǉ�����Ă��܂���
    pause
    exit /b 1
)

:: ���z���̍쐬
if not exist "venv" (
    echo ���z�����쐬���Ă��܂�...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ���z���̍쐬�Ɏ��s���܂���
        pause
        exit /b 1
    )
)

:: ���z����L����
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ���z���̗L�����Ɏ��s���܂���
    pause
    exit /b 1
)

:: �ˑ��p�b�P�[�W�̃C���X�g�[��
echo �ˑ��p�b�P�[�W���C���X�g�[�����Ă��܂�...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo �Z�b�g�A�b�v���������܂����I
    echo �A�v���P�[�V�������N������ɂ� run.bat �����s���Ă�������
) else (
    echo �ˑ��p�b�P�[�W�̃C���X�g�[�����ɃG���[���������܂���
)

pause