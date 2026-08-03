@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
if "%SPHINXAUTOBUILD%" == "" (
	set SPHINXAUTOBUILD=sphinx-autobuild
)
set SOURCEDIR=.
set BUILDDIR=_build
set CONFIGDIR=.
if "%AUTOBUILDOPTS%" == "" (
	set AUTOBUILDOPTS=--ignore _build/*
)

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help
if "%1" == "livehtml" goto livehtml

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% -c %CONFIGDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% -c %CONFIGDIR% %SPHINXOPTS% %O%
goto end

:livehtml
%SPHINXAUTOBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-autobuild' command was not found. Install docs group first:
	echo.  pip install -e . --group docs
	echo.
	exit /b 1
)

%SPHINXBUILD% -M clean %SOURCEDIR% %BUILDDIR% -c %CONFIGDIR% %SPHINXOPTS% %O%
if errorlevel 1 exit /b 1

%SPHINXAUTOBUILD% %AUTOBUILDOPTS% -b html -E -a %SOURCEDIR% %BUILDDIR%\html -c %CONFIGDIR% %SPHINXOPTS% %O%

:end
popd
