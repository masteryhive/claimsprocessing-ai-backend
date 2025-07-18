from typing import List
from pydantic import BaseModel
from src.pipelines.cost_benchmarking import AnalysisModel


def analysis_result_formatter(conditions: list, updated_parsed_list: List[list], results: List[AnalysisModel]) -> str:

    grouped_items = {}
    res_index = 0

    for parsed in updated_parsed_list:
        # Check if the parsed list has an extra numeric value (price) as the last element.
        if len(parsed) >= 4 and isinstance(parsed[-1], (int, float)):
            # For four-element entries, use the provided conditions in order without any mapping.
            base_desc = parsed[0]
            part = parsed[2]
            for cond in conditions:
                if cond == "tokunbo":
                    cond="fairly-used"
                item_text = f"{base_desc} - {cond.upper()}:\n{results[res_index].result}"
                res_index += 1
                key = (base_desc, part)
                if key not in grouped_items:
                    grouped_items[key] = []
                grouped_items[key].append(item_text)
        else:
            # For the original three-element format, check for condition keywords in the description.
            base_desc = parsed[0].split(f' {conditions[0]}')[0].split(f' {conditions[1]}')[0]
            # Use the last element unless it is numeric, then use the second-last.
            if isinstance(parsed[-1], (int, float)) and len(parsed) >= 2:
                part = parsed[-2]
            else:
                part = parsed[-1]
            # Instead of simply uppercasing conditions[0] when found, map it to "FAIRLY-USED".
            if conditions[0].lower() in parsed[0].lower():
                cond = "FAIRLY-USED"
            else:
                cond = conditions[1].upper()
            item_text = f"{base_desc} - {cond}:\n{results[res_index].result}"
            res_index += 1
            key = (base_desc, part)
            if key not in grouped_items:
                grouped_items[key] = []
            grouped_items[key].append(item_text)

    output_lines = []
    i = 1
    for (base_desc, part), items in grouped_items.items():
        group_output = f"{i}. {part}\n" + "\n\n==========\n\n".join(items)
        output_lines.append(group_output)
        i += 1
    return "\n\n".join(output_lines)
