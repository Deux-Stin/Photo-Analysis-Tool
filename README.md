# Photos Analysis Tool

## Description

The Photos Analysis Tool is a Python-based application that allows users to visualize and analyze metadata from their photo collections. The application supports filtering by various camera settings, such as aperture, ISO, shutter speed, focal length and provides dynamic graphs to display the results.

## Features

- **Multi-Brand Support**: Filter photos by camera brands.
- **Date Range Filtering**: Visualize photos taken within a specific date range.
- **Graphical Visualization**: Choose between bar graphs and line graphs to display your data.
- **Aperture, ISO, Shutter Speed, Focal Length Filtering**: Adjust filters to narrow down the photo selection.
- **Responsive UI**: Dynamic updates to the interface based on user input.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/deux-stin/photos-analysis-tool
    ```
2. Navigate to the project directory:
    ```bash
    cd Photo-Analysis-Tool
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Add dependencies for exiftool. Need to be executed in a powershell window
    ```
    powershell -ExecutionPolicy Bypass -File ./exiftool_path_setup.ps1
    ```

## Usage

1. Run the application:
    ```bash
    python main.py
    ```
2. Select the folder containing your photos.
3. Use the filters to refine your photo selection.
4. View the results in the dynamic graph.

## Contributing

Feel free to fork this repository, make your changes, and submit a pull request. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
