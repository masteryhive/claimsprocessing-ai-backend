import pytest
from playwright.sync_api import Page, sync_playwright
from bs4 import BeautifulSoup
from src.teams.resources.cost_benchmarking import CostBenchmarkingPlaywright

@pytest.fixture
def mock_credentials():
    return {
        'email': 'test@example.com',
        'password': 'test_password'
    }

@pytest.fixture
def benchmarking(mock_credentials):
    return CostBenchmarkingPlaywright(mock_credentials['email'], mock_credentials['password'])

@pytest.fixture
def mock_price_data():
    return [10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]

class TestCostBenchmarkingPlaywright:
    def test_initialization(self, mock_credentials):
        benchmarking = CostBenchmarkingPlaywright(mock_credentials['email'], mock_credentials['password'])
        assert benchmarking.email == mock_credentials['email']
        assert benchmarking.password == mock_credentials['password']
        assert benchmarking.playwright is None
        assert benchmarking.browser is None
        assert benchmarking.context is None
        assert benchmarking.page is None

    @pytest.mark.integration
    def test_create_driver(self, benchmarking):
        try:
            page = benchmarking.create_driver()
            assert isinstance(page, Page)
            assert benchmarking.playwright is not None
            assert benchmarking.browser is not None
            assert benchmarking.context is not None
        finally:
            benchmarking.close_driver()

    def test_analyze_price_realism(self, benchmarking, mock_price_data):
        quoted_price = 30000
        result = benchmarking.new_analyze_price_realism(mock_price_data, quoted_price)
        
        assert isinstance(result, dict)
        assert 'is_realistic' in result
        assert 'analysis' in result
        assert isinstance(result['analysis'], dict)
        
        analysis = result['analysis']
        expected_keys = ['mean_price', 'median_price', 'std_dev', 'z_score', 
                        'quoted_price_percentile', 'is_outlier', 'price_range']
        
        for key in expected_keys:
            assert key in analysis

    def test_get_expected_price_range(self, benchmarking, mock_price_data):
        price_range = benchmarking.get_expected_price_range(mock_price_data)
        assert isinstance(price_range, str)
        assert '-' in price_range
        
        # Extract and verify the range values
        lower, upper = map(lambda x: int(x.replace(',', '')), price_range.split(' - '))
        assert lower < upper
        assert lower >= min(mock_price_data)
        assert upper <= max(mock_price_data)

    def test_item_cost_analysis(self, benchmarking, mock_price_data):
        quoted_price = "30,000"
        result = benchmarking.item_cost_analysis(mock_price_data, quoted_price)
        
        assert isinstance(result, str)
        assert "Analysis for quoted price" in result
        assert "median_price" in result
        assert "realistic_price_range" in result
        assert "quoted_price_percentile" in result
        assert "status" in result

    def test_run_with_expected_range(self, benchmarking, mock_price_data):
        search_term = "test item"
        result = benchmarking.run_with_expected_range(search_term, mock_price_data)
        
        assert isinstance(result, str)
        assert search_term in result
        assert "Expected price range" in result

    @pytest.mark.integration
    def test_fetch_market_data_integration(self, benchmarking):
        try:
            prices = benchmarking.fetch_market_data("hyundai side mirror")
            assert isinstance(prices, list)
            if prices:  # If we got results
                assert all(isinstance(price, int) for price in prices)
        finally:
            benchmarking.close_driver()

    def test_close_driver(self, benchmarking):
        # First create a driver
        benchmarking.create_driver()
        
        # Then close it
        benchmarking.close_driver()
        
        # Verify everything is closed
        assert benchmarking.page is None
        assert benchmarking.context is None
        assert benchmarking.browser is None
        assert benchmarking.playwright is None
