@echo off
setlocal

echo �A�v���P�[�V�������N�����Ă��܂�...

:: ���z�������݂��邩�m�F
if not exist "venv" (
    echo ���z����������܂���B�ŏ��� setup.bat �����s���Ă�������
    pause
    exit /b 1
)

:: ���z����L����
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ���z���̗L�����Ɏ��s���܂���
    pause
    exit /b 1
)

:: ���C���X�N���v�g�����s
python src\full_pipline_gui.py

:: �G���[�����������ꍇ�ɃE�B���h�E����Ȃ�
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo �G���[���������܂����B�G���[���b�Z�[�W���m�F���Ă�������
    pause
)