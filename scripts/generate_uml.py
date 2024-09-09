import os
import subprocess

def generate_uml():
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Créer le répertoire 'uml' s'il n'existe pas
    uml_dir = os.path.join(project_root,'..', 'uml')
    os.makedirs(uml_dir, exist_ok=True)

    # Supprimer les fichiers existants pour éviter les conflits
    dot_files = ["classes_photo_analysis.dot", "packages_photo_analysis.dot"]
    png_files = ["classes_photo_analysis.png", "packages_photo_analysis.png"]

    for file in dot_files + png_files:
        file_path = os.path.join(uml_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Utiliser pyreverse pour analyser le projet et générer les fichiers Dot dans 'uml'
    subprocess.run(["pyreverse", "-o", "dot", "-p","photo_analysis", "main", "scripts"])
    os.rename("classes_photo_analysis.dot", os.path.join(uml_dir, "classes_photo_analysis.dot"))
    os.rename("packages_photo_analysis.dot", os.path.join(uml_dir, "packages_photo_analysis.dot"))

    # Convertir les fichiers Dot en PNG et les enregistrer dans 'uml'
    subprocess.run(["dot", "-Tpng", os.path.join(uml_dir, "classes_photo_analysis.dot"), "-o", os.path.join(uml_dir, "classes_photo_analysis.png")])
    subprocess.run(["dot", "-Tpng", os.path.join(uml_dir, "packages_photo_analysis.dot"), "-o", os.path.join(uml_dir, "packages_photo_analysis.png")])

    print("Diagrammes générés : uml/classes_photo_analysis.png et uml/packages_photo_analysis.png")
    
    # Supprimer les fichiers existants pour éviter les conflits
    dot_files = ["classes_photo_analysis.dot", "packages_photo_analysis.dot"]

    for file in dot_files:
        file_path = os.path.join(uml_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    generate_uml()
