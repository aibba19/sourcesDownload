Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
repoRoot = FSO.GetParentFolderName(WScript.ScriptFullName)
pythonw = repoRoot & "\.venv\Scripts\pythonw.exe"
script = "-m app.main"

If FSO.FileExists(pythonw) Then
    WshShell.CurrentDirectory = repoRoot
    WshShell.Run """" & pythonw & """ " & script, 0, False
Else
    MsgBox "pythonw.exe non trovato in .venv\Scripts. Esegui prima l'installazione dipendenze oppure usa build_exe.bat.", 48, "sourcesDownload"
End If
