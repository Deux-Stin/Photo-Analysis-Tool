class PhotoFilter:
    def __init__(self, date_range=None, folder=None, file_type=None, camera_model=None):
        self.date_range = date_range  # Tuple (start_date, end_date)
        self.folder = folder
        self.file_type = file_type  # e.g., 'jpg', 'png'
        self.camera_model = camera_model  # e.g., 'Canon', 'Nikon'
        
    def apply(self, photos):
        filtered_photos = photos
        if self.date_range:
            filtered_photos = [p for p in filtered_photos if self.date_range[0] <= p['date_taken'] <= self.date_range[1]]
        if self.folder:
            filtered_photos = [p for p in filtered_photos if p['folder_path'] == self.folder]
        if self.file_type:
            filtered_photos = [p for p in filtered_photos if p['filename'].endswith(self.file_type)]
        if self.camera_model:
            filtered_photos = [p for p in filtered_photos if p['camera_model'] == self.camera_model]
        return filtered_photos
