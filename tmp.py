import subprocess
import json

def get_exif_data(image_path):
    # Appel à exiftool pour obtenir les métadatas au format JSON
    result = subprocess.run(['exiftool', '-json', image_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de exiftool: {result.stderr}")
        return None
    
    # Convertir la sortie JSON en dictionnaire Python
    exif_data = json.loads(result.stdout)
    
    # Assurer que l'extrait contient des métadatas
    if not exif_data:
        print("Aucune donnée EXIF trouvée.")
        return None
    
    return exif_data[0]

image_path = r'C:\\Users\\User\\Desktop\\Tmp Images\\debug\\20240607_201030.heic'
metadata = get_exif_data(image_path)

if metadata:
    print("Métadatas de l'image :")
    for key, value in metadata.items():
        print(f"{key}: {value}")


# # Import Libraries
# from PIL import Image
# from PIL.ExifTags import TAGS

# # Open Image
# img=Image.open('C:\\Users\\User\\Desktop\\Tmp Images\\Coord GPS\\20221216_111746.jpg')

# #Get EXIF Data
# exif_table={}
# for k, v in img.getexif().items():
#     tag=TAGS.get(k)
#     exif_table[tag]=v