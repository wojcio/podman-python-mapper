"""
Test suite for the DML Mapper.
Tests parsing and code generation functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mapper import Parser, CodeGenerator, parse_dml_file, generate_python_code


def test_simple_csv_to_csv():
    """Test simple CSV to CSV mapping."""
    dml_code = """
MAPPING simple_test {
    SOURCE CSV {
        file: "input.csv"
    }
    
    TARGET CSV {
        file: "output.csv"
    }
    
    RULES {
        map name -> full_name
        map amount -> total_amount AS decimal
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    assert mapping.name == "simple_test"
    assert mapping.source.type == "CSV"
    assert mapping.target.type == "CSV"
    assert len(mapping.rules) == 2
    
    print("✓ Simple CSV to CSV test passed")
    return mapping


def test_csv_to_xml():
    """Test CSV to XML mapping."""
    dml_code = """
MAPPING csv_to_xml_test {
    SOURCE CSV {
        file: "data.csv"
        has_header: true
    }
    
    TARGET XML {
        file: "output.xml"
        root_element: "Records"
    }
    
    RULES {
        map CustomerID -> Record/CustomerID
        map Name -> Record/Name 
            TRANSFORM trim()
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    assert mapping.name == "csv_to_xml_test"
    assert len(mapping.rules) == 2
    
    # Generate Python code
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    assert "execute_mapping" in python_code
    assert "transform_value" in python_code
    
    print("✓ CSV to XML test passed")
    print(f"Generated {len(python_code)} bytes of Python code")
    return mapping


def test_with_transformations():
    """Test mapping with various transformations."""
    dml_code = """
MAPPING transformation_test {
    SOURCE CSV {
        file: "input.csv"
    }
    
    TARGET XML {
        file: "output.xml"
    }
    
    RULES {
        map name -> Name 
            TRANSFORM upper()
        map amount -> Amount
            TRANSFORM format_number("#,##0.00")
        map date -> FormattedDate
            TRANSFORM format_date("DD/MM/YYYY")
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    assert "upper" in python_code.lower()
    assert "format_number" in python_code
    assert "format_date" in python_code
    
    print("✓ Transformation test passed")
    return mapping


def test_with_conditions():
    """Test mapping with conditional rules."""
    dml_code = """
MAPPING condition_test {
    SOURCE CSV {
        file: "input.csv"
    }
    
    TARGET CSV {
        file: "output.csv"
    }
    
    RULES {
        map status -> Status
            IF amount > 1000
                DEFAULT "premium"
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    assert "if" in python_code.lower()
    
    print("✓ Condition test passed")
    return mapping


def test_db_source():
    """Test database source configuration."""
    dml_code = """
MAPPING db_test {
    SOURCE DB {
        type: "sqlite"
        connection_string: "test.db"
        query: "SELECT * FROM users"
    }
    
    TARGET CSV {
        file: "output.csv"
    }
    
    RULES {
        map id -> ID AS integer
        map name -> Name
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    assert mapping.source.type == "DB"
    assert mapping.source.config["type"] == "sqlite"
    
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    assert "read_db_source" in python_code
    
    print("✓ DB source test passed")
    return mapping


def test_xml_target():
    """Test XML target configuration."""
    dml_code = """
MAPPING xml_target_test {
    SOURCE CSV {
        file: "input.csv"
    }
    
    TARGET XML {
        file: "output.xml"
        root_element: "Data"
    }
    
    RULES {
        map id -> Item/id
        map value -> Item/value
    }
}
"""
    
    parser = Parser(dml_code)
    mapping = parser.parse()
    
    generator = CodeGenerator(mapping)
    python_code = generator.generate()
    
    assert "write_xml_output" in python_code
    assert "ET.ElementTree" in python_code
    
    print("✓ XML target test passed")
    return mapping


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running DML Mapper Tests")
    print("=" * 50)
    
    tests = [
        test_simple_csv_to_csv,
        test_csv_to_xml,
        test_with_transformations,
        test_with_conditions,
        test_db_source,
        test_xml_target,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)