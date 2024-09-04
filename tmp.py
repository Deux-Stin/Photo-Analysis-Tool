class DataVisualizer(QWidget):
    def __init__(self, db_path, directory):
        super().__init__()
        self.db_path = db_path
        self.directory = directory
        self.data_loader = DataLoader(db_path)
        self.param_ranges = self.data_loader.get_parameter_ranges()

        self.init_ui()
        self.load_folders()  # Charger les dossiers et mettre à jour les marques
        self.update_plot()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.folder_filter = QComboBox(self)
        self.folder_filter.addItem("All")
        main_layout.addWidget(self.folder_filter)

        content_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        # Filters section
        self.filters_group = QGroupBox("Filters", self)
        filters_layout = QFormLayout()

        # Filter by Brand (using CheckBoxes)
        filters_layout.addRow(QLabel("Brands:"))
        self.brand_filter_box = QVBoxLayout()
        self.brand_filters = {}  # Dictionnaire pour stocker les QCheckBox
        filters_layout.addRow(self.brand_filter_box)

        # Initial load of brands based on all folders
        self.load_brands()  # Charger les marques pour "All"

        self.filters_group.setLayout(filters_layout)
        left_layout.addWidget(self.filters_group)

        # ... (Autres composants d'interface)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Connect signals for filters
        self.folder_filter.currentIndexChanged.connect(self.update_brands_and_plot)

        for checkbox in self.brand_filters.values():
            checkbox.stateChanged.connect(self.update_plot)

    def load_folders(self):
        data = self.data_loader.get_folders()
        self.folder_filter.addItems(data['folders_with_images'])
        return data

    def load_brands(self, folder=None):
        # Efface les cases à cocher existantes
        for i in reversed(range(self.brand_filter_box.count())):
            widget = self.brand_filter_box.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Charge les marques depuis la base de données en fonction du dossier
        brands = self.data_loader.get_brands(folder)
        self.brand_filters.clear()

        for brand in brands:
            checkbox = QCheckBox(brand)
            self.brand_filters[brand] = checkbox
            self.brand_filter_box.addWidget(checkbox)
            checkbox.stateChanged.connect(self.update_plot)

    def update_brands_and_plot(self):
        selected_folder = self.folder_filter.currentText()
        if selected_folder == "All":
            self.load_brands()  # Charger toutes les marques
        else:
            self.load_brands(folder=selected_folder)  # Charger les marques pour le dossier sélectionné

        self.update_plot()

    def update_plot(self):
        selected_folder = self.folder_filter.currentText()
        selected_brands = [brand for brand, checkbox in self.brand_filters.items() if checkbox.isChecked()]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            base_query = "SELECT column_name, COUNT(*) FROM photos WHERE 1=1"
            params = []

            # Application du filtre de dossier
            if selected_folder != "All":
                base_query += " AND folder_path = ?"
                params.append(selected_folder)

            # Application du filtre de marques
            if selected_brands:
                base_query += " AND brand_name IN ({})".format(", ".join('?' for _ in selected_brands))
                params.extend(selected_brands)

            # Application des autres filtres (exemple : ouverture)
            min_aperture = self.aperture_filter.slider_min.value() / self.factor
            max_aperture = self.aperture_filter.slider_max.value() / self.factor
            base_query += " AND aperture >= ? AND aperture <= ?"
            params.extend([min_aperture, max_aperture])

            # Filtre ISO, vitesse d'obturation, focale, etc. (comme dans votre code original)
            # ...

            # Finalisation de la requête
            base_query += " GROUP BY column_name ORDER BY column_name"
            cursor.execute(base_query, params)
            data = cursor.fetchall()

            # Mise à jour du graphique
            # ...
