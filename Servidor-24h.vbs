' Runs Servidor-24h.ps1 without opening a window (used by the scheduled task).
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & dir & "\Servidor-24h.ps1""", 0, True
