#!/usr/bin/env python3
"""
Test script for table formatting functionality
"""

from table_formatter import format_table

def test_format_table():
    """Test table formatting logic"""
    
    # Test 1: Pipe separators with manual header separator
    test_input_1 = """Name | Age | City
---- | --- | ----
John | 25 | New York
Jane | 30 | Los Angeles"""
    expected_output_1 = """+------+-----+-------------+
| Name | Age | City        |
+======+=====+=============+
| John | 25  | New York    |
| Jane | 30  | Los Angeles |
+------+-----+-------------+"""
    
    print("Test 1 - Pipe separators with manual header:")
    print("Input:\n", test_input_1)
    formatted_output_1 = format_table(test_input_1)
    print("Formatted Output:\n", formatted_output_1)
    print("Expected Output:\n", expected_output_1)
    assert formatted_output_1 == expected_output_1, "Test 1 Failed"
    print("Test 1 Passed\n" + "="*50 + "\n")
    
    # Test 2: Whitespace separators with manual header separator
    test_input_2 = """Name  Age  City
----  ---  ----
John  25   New York
Jane  30   Los Angeles"""
    expected_output_2 = """+------+-----+-------------+
| Name | Age | City        |
+======+=====+=============+
| John | 25  | New York    |
| Jane | 30  | Los Angeles |
+------+-----+-------------+"""
    
    print("Test 2 - Whitespace separators with manual header:")
    print("Input:\n", test_input_2)
    formatted_output_2 = format_table(test_input_2)
    print("Formatted Output:\n", formatted_output_2)
    print("Expected Output:\n", expected_output_2)
    assert formatted_output_2 == expected_output_2, "Test 2 Failed"
    print("Test 2 Passed\n" + "="*50 + "\n")
    
    # Test 3: Markdown-style pipes with manual header separator
    test_input_3 = """| Name | Age | City |
| ---- | --- | ---- |
| John | 25 | New York |
| Jane | 30 | Los Angeles |"""
    expected_output_3 = """+------+-----+-------------+
| Name | Age | City        |
+======+=====+=============+
| John | 25  | New York    |
| Jane | 30  | Los Angeles |
+------+-----+-------------+"""
    
    print("Test 3 - Markdown-style pipes with manual header:")
    print("Input:\n", test_input_3)
    formatted_output_3 = format_table(test_input_3)
    print("Formatted Output:\n", formatted_output_3)
    print("Expected Output:\n", expected_output_3)
    assert formatted_output_3 == expected_output_3, "Test 3 Failed"
    print("Test 3 Passed\n" + "="*50 + "\n")
    
    # Test 4: Without header separator (no automatic header)
    test_input_4 = """Name | Age | City
John | 25 | New York"""
    expected_output_4 = """+------+-----+----------+
| Name | Age | City     |
| John | 25  | New York |
+------+-----+----------+"""
    
    print("Test 4 - Without header separator (no automatic header):")
    print("Input:\n", test_input_4)
    formatted_output_4 = format_table(test_input_4)
    print("Formatted Output:\n", formatted_output_4)
    print("Expected Output:\n", expected_output_4)
    assert formatted_output_4 == expected_output_4, "Test 4 Failed"
    print("Test 4 Passed\n" + "="*50 + "\n")

    # Test 5: Input from user's problem description
    test_input_5 = """|test|ohhhhh|
|hmmm coool|yes!!|
----
|I|Like|
----"""
    expected_output_5 = """+------------+--------+
| test       | ohhhhh |
| hmmm coool | yes!!  |
+------------+--------+
| I          | Like   |
+------------+--------+"""

    print("Test 5 - User's problem description input:")
    print("Input:\n", test_input_5)
    formatted_output_5 = format_table(test_input_5)
    print("Formatted Output:\n", formatted_output_5)
    print("Expected Output:\n", expected_output_5)
    assert formatted_output_5 == expected_output_5, "Test 5 Failed"
    print("Test 5 Passed\n" + "="*50 + "\n")


    print("All table formatting tests passed!")

if __name__ == "__main__":
    test_format_table()