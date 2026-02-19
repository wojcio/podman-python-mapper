#!/usr/bin/env python3
# Data Mapping: csv_to_xml_test

import xml.etree.ElementTree as ET
import csv

# Transformation Functions
def transform_value(value, func_name: str):
    """Apply transformation function to value."""
    if value is None:
        return None
    try:
        if func_name == "upper":
            return str(value).upper()
        elif func_name == "lower":
            return str(value).lower()
        elif func_name == "trim":
            return str(value).strip()
        elif func_name == "int":
            return int(value)
        elif func_name == "float":
            return float(value)
    except Exception:
        pass
    return value

def read_source(file_path: str) -> List[Dict]:
    """Read CSV file."""
    items = []
    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(dict(row))
    return items

def write_target(items: List[Dict], output_path: str):
    """Write XML file."""
    root = ET.Element("Root")
    for item in items:
        elem = ET.SubElement(root, "Item")
        for key, value in item.items():
            child = ET.SubElement(elem, key)
            child.text = str(value) if value else ""
    ET.ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)

def execute_mapping(input_file: str, output_file: str) -> List[Dict]:
    """Execute the mapping."""
    source_items = read_source(input_file)
    output_items = []
    for item in source_items:
        output_item = {
            "RecordCustomerID": item.get("CustomerID"),
            "RecordCustomerName": item.get("CustomerName"),
            "RecordOrderDate": item.get("OrderDate")
        }
        output_items.append(output_item)
    write_target(output_items, output_file)
    return output_items

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        result = execute_mapping(sys.argv[1], sys.argv[2])
        print(f"Done: {len(result)} items")
    else:
        print("Usage: python mapper.py <input> <output>")