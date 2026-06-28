@echo off
title projectTP RUNNING - DO NOT CLOSE
echo.
echo   projectTP is RUNNING
echo   Unreal Editor and MCP server port 8000 are active
echo   DO NOT CLOSE THIS WINDOW. You can minimize it.
echo.
"D:\unreal\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "D:\unreal\projectTP\projectTP.uproject" -ExecCmds="ModelContextProtocol.StartServer 8000"
