# Automated Data Analysis

## Overview
The **Automated Data Analysis** script simplifies the process of analyzing datasets by performing key statistical operations and generating insights using an LLM (Large Language Model). The script handles the analysis of CSV files, generates visualizations, and creates an insightful report based on the dataset provided.

## Features
- Automatically detects the encoding of CSV files.
- Generates summary statistics for numerical columns.
- Identifies and reports missing values.
- Calculates the correlation matrix and creates a heatmap visualization.
- Uses an LLM to provide statistical insights and narrative reports.
- Outputs a comprehensive README with analysis results and visualizations.

## Prerequisites
1. **Python Version**: Ensure Python 3.11 or above is installed.
2. **API Token**: Set the `AIPROXY_TOKEN` environment variable for accessing the LLM.

To set the environment variable:
```bash
export AIPROXY_TOKEN=<your_token_here>
```

## Usage
Run the script with the following command:

```bash
python automated_analysis.py <path_to_csv_file>
```

### Example:
```bash
python automated_analysis.py data/sample_dataset.csv
```

### Output:
- A folder will be created using the name of the dataset file (without the extension).
- Inside this folder:
  - **`README.md`**: Contains detailed insights and analysis.
  - **`correlation_matrix.png`**: Heatmap visualization of the correlation matrix.

## Folder Structure
```plaintext
|-- automated_data_analysis/
    |-- automated_analysis.py
    |-- requirements.txt
    |-- README.md (this file)
    |-- <dataset_folder>/
        |-- README.md
        |-- correlation_matrix.png
```

## Example Outputs
### Statistical Insights:
- Summary statistics for numerical columns.
- Missing value counts for each column.
- Key observations about correlations.

### Visualizations:
- **Correlation Heatmap**: A visual representation of relationships between numerical features.

## Error Handling
The script handles common issues such as:
- Missing API tokens.
- File encoding errors.
- Network timeouts or rate limits during API calls.

If an error occurs, descriptive messages are logged to the console.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

Developed with ❤️ by Jay Thadeshwar.

