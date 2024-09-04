# # Définir le chemin d'ExTool
# $exiftoolPath = "C:\Users\User\Desktop\Formation Python\Photos-Analysis-Tool\exiftool-12.93_64"

# # Ajouter le chemin à la variable d'environnement PATH
# [System.Environment]::SetEnvironmentVariable("Path", "$env:Path;$exiftoolPath", [System.EnvironmentVariableTarget]::Machine)

# Write-Host "Le chemin a été ajouté à PATH avec succès."


# Définir le chemin d'ExTool de manière dynamique
$exiftoolPath = Join-Path $PSScriptRoot "exiftool-12.93_64"

# Ajouter le chemin à la variable d'environnement PATH
[System.Environment]::SetEnvironmentVariable("Path", "$env:Path;$exiftoolPath", [System.EnvironmentVariableTarget]::Machine)

Write-Host "Le chemin a été ajouté à PATH avec succès."
