# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "requests",
#   "seaborn",
#   "matplotlib",
#   "ipykernel",
#   "chardet",
# ]
# ///

import argparse
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import chardet
import requests
import signal
from requests.adapters import HTTPAdapter, Retry
from contextlib import contextmanager
import time

# Global API Token
API_KEY = os.environ["AIPROXY_TOKEN"]
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

# Check if API Token is available
if not API_KEY:
    raise EnvironmentError("AIPROXY_TOKEN not found in environment variables. Please set it before running the script.")

# Set a timeout for the script
@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError(f"Script execution exceeded the time limit of {seconds} seconds.")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Function to handle API requests with retry logic
def call_api(prompt):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        # Retry strategy
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))

        # Send the API request
        response = session.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err} (Status Code: {response.status_code})"
        print(f"[ERROR] {error_msg}")
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "Error: Request timed out. The server took too long to respond."
        print(f"[ERROR] {error_msg}")
        return error_msg
    except Exception as err:
        error_msg = f"Error occurred: {err}"
        print(f"[ERROR] {error_msg}")
        return error_msg

# Main script execution
if __name__ == "__main__":
    start_time = time.time()

    # Argument parsing
    parser = argparse.ArgumentParser(description="Automated dataset analysis.")
    parser.add_argument("csv_file", type=str, help="Path to the CSV dataset.")
    args = parser.parse_args()
    csv_file = args.csv_file

    # Folder creation
    folder_name = os.path.splitext(os.path.basename(csv_file))[0]
    os.makedirs(folder_name, exist_ok=True)

    try:
        # Detect encoding and read CSV
        print("[INFO] Detecting file encoding...")
        with open(csv_file, 'rb') as f:
            encoding = chardet.detect(f.read())['encoding']

        print(f"[INFO] Loading dataset with detected encoding: {encoding}...")
        data = pd.read_csv(csv_file, encoding=encoding)
    except Exception as e:
        print(f"[ERROR] Failed to load CSV file: {e}")
        exit(1)

    try:
        with time_limit(120):
            # Generate statistical analysis
            print("[INFO] Generating statistical summaries...")
            numeric_data = data.select_dtypes(include=['number'])
            summary = numeric_data.describe()
            missing_values = data.isnull().sum()
            correlation_matrix = numeric_data.corr()

            # Save heatmap
            print("[INFO] Creating correlation matrix heatmap...")
            # heatmap_path = os.path.join(img_folder, "correlation_matrix.png")
            heatmap_path = os.path.join(folder_name, "correlation_matrix.png")
            sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
            plt.title("Correlation Matrix Heatmap")
            plt.tight_layout()
            plt.savefig(heatmap_path, dpi=100, bbox_inches='tight')
            plt.close()

            # Prompts for AI analysis
            print("[INFO] Preparing prompts for LLM analysis...")
            prompt_dynamic = f"""
            You are a Data Analyst. I am providing information about data. Analyze it and provide insights.

            Dataset columns:
            {list(data.columns)}

            Summary statistics:
            {summary}

            Missing values:
            {missing_values}

            Based on this info kindly provide prompt that can be used to analyse csv file by llm.
            And follow format for response.
            I will provide only your response in  next prompt.
            Formate: 
            first provide above info as it is and then write a prompt in less than 4 line.
            also add in prompt that 'do not return any code in response'
            """
            
            print("[INFO] Asking LLM for a dynamic prompt...")
            dynamic_prompt = call_api(prompt_dynamic)
            # print(f"[INFO] Generated dynamic prompt: {dynamic_prompt}")

            # Use the dynamic prompt for further analysis
            print("[INFO] Sending dynamic prompt to LLM...")
            dynamic_analysis = call_api(dynamic_prompt)

            prompt_corr = f"""
            The correlation matrix is:
            {correlation_matrix}

            Provide insights based on the correlation matrix:
            Use the following format:
            1. Briefly summarize the data.
            2. Provide insights in bullet points.
            3. Conclude your analysis.

            ![Correlation Matrix](correlation_matrix.png)
            """

            prompt_story = f"""
            You are an experienced data storyteller. Based on the results and analysis provided from the dataset, craft a comprehensive narrative that conveys key findings, trends, and actionable insights. Use the following structure to frame the story:  
            
            1. **Introduction to the Data**:  
            2. **Key Findings from Statistical Analysis**:  
            3. **Insights from Correlation Matrix**:  
            4. **Trends and Patterns**:  
            5. **Implications and Recommendations**:  
            6. **Conclusion**:  
            Be concise yet informative, ensuring that the narrative is engaging and easy for a general audience to understand. Use bullet points or short paragraphs wherever necessary to improve clarity. Include real-world examples if relevant.  
            """

            # Call LLM for insights
            print("[INFO] Sending data to LLM for analysis...")
            insights1 = call_api(dynamic_prompt)
            insights2 = call_api(prompt_corr)
            insights3 = call_api(prompt_story)

            # Save analysis to README
            print("[INFO] Writing insights to README.md...")
            readme_path = os.path.join(folder_name, "README.md")
            with open(readme_path, "w") as f:
                f.write("# Automated Analysis Report\n")
                f.write(f"## Dataset: {csv_file}\n\n")
                f.write("### Statistical Insights\n")
                f.write((insights1 if "Error" not in insights1 else f"Error: {insights1}") + "\n")
                f.write("### Correlation Insights\n")
                f.write((insights2 if "Error" not in insights2 else f"Error: {insights2}") + "\n")
                f.write("### Story\n")
                f.write((insights3 if "Error" not in insights3 else f"Error: {insights3}") + "\n")
                f.write("### Visualizations\n")
                f.write(f"![Correlation Matrix](correlation_matrix.png)\n")

    except TimeoutError as te:
        print(f"[ERROR] {te}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

    end_time = time.time()
    print(f"[INFO] Script execution completed in {end_time - start_time:.2f} seconds.")
