# Définir le chemin d'ExifTool de manière dynamique en fonction du répertoire du script
$exiftoolPath = Join-Path $PSScriptRoot "exiftool-12.93_64"

# Ajouter le chemin à la variable d'environnement PATH
[System.Environment]::SetEnvironmentVariable("Path", "$env:Path;$exiftoolPath", [System.EnvironmentVariableTarget]::Machine)

Write-Host "Le chemin '$exiftoolPath' a été ajouté à PATH avec succès."

