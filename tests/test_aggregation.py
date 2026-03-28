
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser import Parser, CodeGenerator

def test_aggregation_parsing():
    dml_code = """
    MAPPING agg_test {
        SOURCE CSV { file: "sales.csv" }
        TARGET CSV { file: "summary.csv" }
        AGGREGATE {
            GROUP BY region, category
            RULES {
                map amount -> total_sales TRANSFORM sum(amount)
                map amount -> average_sale TRANSFORM avg(amount)
                map id -> transaction_count TRANSFORM count(id)
            }
        }
    }
    """
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    assert mapping.name == "agg_test"
    assert mapping.aggregate is not None
    assert mapping.aggregate.group_by == ["region", "category"]
    assert len(mapping.aggregate.rules) == 3
    
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    print("Generated Code:")
    print(python_code)
    
    assert "grouped_data = {}" in python_code
    assert "sum(float(item.get(\"amount\", 0)) for item in group)" in python_code
    assert "len(group)" in python_code
    
    print("Test passed!")

if __name__ == "__main__":
    test_aggregation_parsing()
