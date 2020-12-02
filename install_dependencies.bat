for /F "tokens=*" %%A in (requirements.txt) do pip install %%A
pause