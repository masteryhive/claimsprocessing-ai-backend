from typing import List
from pydantic import BaseModel
from src.pipelines.cost_benchmarking import AnalysisModel

# Function to format Analysis result list   
def analysis_result_formatter(conditions:list, updated_parsed_list:List[list],results:List[AnalysisModel])->str:
    condition_result = []

    # Group items by base description (before condition)
    grouped_items = {}
    for parsed_list, result in zip(updated_parsed_list, results):
        base_desc = parsed_list[0].split(f' {conditions[0]}')[0].split(f' {conditions[1]}')[0]
        if base_desc not in grouped_items:
            grouped_items[base_desc] = []
        grouped_items[base_desc].append((parsed_list[0], result.result))

    # Process grouped items
    for i, (base_desc, items) in enumerate(grouped_items.items(), 1):
        group_results = []
        for item, result in items:
            condition = conditions[0].upper() if conditions[0] in item else conditions[1].upper()
            group_results.append(f"{base_desc} - {condition}:\n{result}")
        
        condition_result.append(f"{i}. " + "\n\n==========\n\n".join(group_results))
    
    return "\n\n".join(condition_result)
