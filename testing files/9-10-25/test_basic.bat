@echo off
echo Starting basic test... > test_output.txt
echo %DATE% %TIME% >> test_output.txt
echo. >> test_output.txt

echo Creating test file... >> test_output.txt
echo This is a test file. > test_file.txt 2>> test_output.txt

echo. >> test_output.txt
echo Directory listing: >> test_output.txt
dir /b >> test_output.txt 2>&1

echo. >> test_output.txt
echo Test complete. Check test_output.txt for results.
