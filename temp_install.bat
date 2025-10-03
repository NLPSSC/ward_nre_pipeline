@echo off 
setlocal enabledelayedexpansion 
for /f "usebackq tokens=1,2 delims==" %%A in (".env") do ( 
  set "var=%%A" 
  set "val=%%B" 
  for /f "tokens=* delims= " %%x in ("!val!") do set "!var!=%%x" 
) 
call scripts\quickumls_subset_install.bat "%UMLS_SUBSET_SOURCE%" "%QUICKUMLS_DATA%" 
