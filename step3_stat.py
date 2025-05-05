import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

def calculate_stats():
    # Path to the CSV file
    csv_path = Path("result/eval/eval_pairs.csv")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Group by model and prompt type
    grouped_data = defaultdict(lambda: defaultdict(list))
    
    # Categories to track
    categories = ["DCE", "TVM", "STOKE", "OJ_A", "OJ_V", "OJ_VA"]
    
    # Process each row
    for _, row in df.iterrows():
        model = row['eval_model'].split('/')[-1]
        prompt_type = row['eval_prompt_type']
        category = row['category']
        accuracy = row['stat_accuracy']
        
        # Create a key for model and prompt type
        model_prompt_key = f"{model} ({prompt_type})"
        
        # Add accuracy to the appropriate category
        if category in categories:
            grouped_data[model_prompt_key][category].append(accuracy)
    
    # Calculate averages and format results
    results = []
    
    # Define column widths for better alignment
    model_width = max(len(model_prompt) for model_prompt in grouped_data.keys()) + 2
    category_width = 8  # Width for category columns (DCE, TVM, etc.)
    
    # Format the header
    header = (f"{'Model':<{model_width}} | "
              f"{'DCE':<{category_width}} | "
              f"{'CUDA':<{category_width}} | " # TVM -> CUDA
              f"{'x86-64':<{category_width}} | " # STOKE -> x86-64
              f"{'OJ_A':<{category_width}} | "
              f"{'OJ_V':<{category_width}} | "
              f"{'OJ_VA':<{category_width}} | "
              f"{'Overall Accuracy'}")
    
    separator = "-" * len(header)
    
    # Calculate averages for each model and prompt type
    for model_prompt, category_data in grouped_data.items():
        row_data = [f"{model_prompt:<{model_width}}"]
        category_averages = []
        
        for category in categories:
            if category in category_data and category_data[category]:
                avg = 100 * sum(category_data[category]) / len(category_data[category])
                category_averages.append(avg)
                row_data.append(f"{avg:.1f}%".ljust(category_width))
            else:
                row_data.append("-".ljust(category_width))
                
        # Calculate overall average
        if category_averages:
            overall_avg = sum(category_averages) / len(category_averages)
            row_data.append(f"{overall_avg:.1f}%")
        else:
            row_data.append("-")
            
        results.append(row_data)
    
    # Print the results
    print(header)
    print(separator)
    for row in results:
        print(" | ".join(row))

if __name__ == "__main__":
    calculate_stats()
