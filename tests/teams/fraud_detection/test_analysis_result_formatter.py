import unittest
from typing import List

from src.teams.fraud_detection.helper import analysis_result_formatter

# Dummy AnalysisModel class for testing purposes
class AnalysisModel:
    def __init__(self, result: str, priceRange: str):
        self.result = result
        self.priceRange = priceRange


class TestAnalysisResultFormatter(unittest.TestCase):
    def test_example_input(self):
        conditions = ['tokunbo', 'brand new']
        updated_parsed_list = [
            ['Hyundai sonata suv tokunbo', 2015, 'side mirror'],
            ['Hyundai sonata suv brand new', 2015, 'side mirror'],
            ['Hyundai sonata SUV tokunbo', 2015, 'door panel'],
            ['Hyundai sonata SUV brand new', 2015, 'door panel']
        ]
        analysis_text = (
            "\nAnalysis for quoted price: 190,000\n"
            "--------------------------------------------------------------\n"
            "median_price: 55,000.00\n"
            "realistic_price_range: 49,500 to 60,500\n"
            "quoted_price_percentile: 100.0th percentile\n"
            "status: ❌ This quoted price appears UNREALISTIC"
        )
        results = [
            AnalysisModel(result=analysis_text, priceRange='53,625 - 56,375'),
            AnalysisModel(result=analysis_text, priceRange='53,625 - 56,375'),
            AnalysisModel(result='no result', priceRange='no price range'),
            AnalysisModel(result='no result', priceRange='no price range')
        ]

        expected_output = (
            "1. side mirror\n"
            "Hyundai sonata suv - FAIRLY-USED:\n"
            "\n"
            "Analysis for quoted price: 190,000\n"
            "--------------------------------------------------------------\n"
            "median_price: 55,000.00\n"
            "realistic_price_range: 49,500 to 60,500\n"
            "quoted_price_percentile: 100.0th percentile\n"
            "status: ❌ This quoted price appears UNREALISTIC\n"
            "\n"
            "==========\n"
            "\n"
            "Hyundai sonata suv - BRAND NEW:\n"
            "\n"
            "Analysis for quoted price: 190,000\n"
            "--------------------------------------------------------------\n"
            "median_price: 55,000.00\n"
            "realistic_price_range: 49,500 to 60,500\n"
            "quoted_price_percentile: 100.0th percentile\n"
            "status: ❌ This quoted price appears UNREALISTIC\n\n"
            "2. door panel\n"
            "Hyundai sonata SUV - FAIRLY-USED:\n"
            "no result\n"
            "\n"
            "==========\n"
            "\n"
            "Hyundai sonata SUV - BRAND NEW:\n"
            "no result"
        )

        output = analysis_result_formatter(conditions, updated_parsed_list, results)
        self.assertEqual(output, expected_output)

    def test_empty_inputs(self):
        # Test with empty lists
        conditions = []
        updated_parsed_list = []
        results = []
        output = analysis_result_formatter(conditions, updated_parsed_list, results)
        self.assertEqual(output, "")

    def test_single_entry(self):
        # Test with a single entry
        conditions = ['old', 'new']
        updated_parsed_list = [['Car model old', 2020, 'front bumper']]
        analysis_text = "Test analysis result"
        results = [AnalysisModel(result=analysis_text, priceRange='1000 - 2000')]
        expected_output = (
            "1. front bumper\n"
            "Car model - FAIRLY-USED:\n"
            "Test analysis result"
        )
        output = analysis_result_formatter(conditions, updated_parsed_list, results)
        self.assertEqual(output, expected_output)

    def test_mixed_entries(self):
        # Test when some parsed lists use the original three-element format
        # and some use the new four-element format.
        conditions = ['tokunbo', 'brand new']
        updated_parsed_list = [
            ['Hyundai sonata suv tokunbo', 2015, 'side mirror'],
            ['Hyundai elantra SUV', 2015, 'door panel', 70000]
        ]
        results = [
            AnalysisModel(result='analysis A', priceRange='range A'),
            # For the second parsed list, we expect two analysis results:
            AnalysisModel(result='no result', priceRange='no price range'),
            AnalysisModel(result='no result', priceRange='no price range')
        ]
        # Expected output:
        # First group comes from the original three-element list.
        # Second group is produced from the four-element list.
        expected_output = (
            "1. side mirror\n"
            "Hyundai sonata suv - FAIRLY-USED:\n"
            "analysis A\n\n"
            "2. door panel\n"
            "Hyundai elantra SUV - FAIRLY-USED:\n"
            "no result\n\n"
            "==========\n\n"
            "Hyundai elantra SUV - BRAND NEW:\n"
            "no result"
        )
        output = analysis_result_formatter(conditions, updated_parsed_list, results)

        self.assertEqual(output, expected_output)

