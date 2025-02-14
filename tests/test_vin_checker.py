import time
import requests
from datetime import datetime
from typing import Dict, Set, List, Optional, Any
from .vin_data import (
    WMI_MAP, 
    VDS_PATTERNS, 
    YEAR_MAP, 
    WEIGHT_FACTORS, 
    TRANSLITERATION, 
    VALID_CHARS
)

class VINValidator:
    def __init__(self) -> None:
        self.wmi_map = WMI_MAP
        self.vds_patterns = VDS_PATTERNS
        self.year_map = YEAR_MAP
        self.weights = WEIGHT_FACTORS
        self.transliteration = TRANSLITERATION
        self.valid_chars = VALID_CHARS
        
        # API configuration
        self.request_timeout: int = 5
        self.max_retries: int = 3
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Validation constants
        self.VIN_LENGTH: int = 17
        self.CHECK_DIGIT_INDEX: int = 8

        self.primary_api_url = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/"
        self.secondary_api_url = "https://api.apiverve.com/v1/vindecoder/decode"
        self.apiverve_key = "YOUR_API_KEY"  # Replace with your actual APIVerve API key

        # Valid world manufacturer regions
        self.valid_regions: Dict[str, str] = {
            'A': 'Africa', 'B': 'Africa', 'C': 'Africa',
            'J': 'Asia', 'K': 'Asia', 'L': 'Asia', 'R': 'Asia',
            'S': 'Europe', 'T': 'Europe', 'U': 'Europe', 'V': 'Europe', 'W': 'Europe', 'X': 'Europe', 'Y': 'Europe', 'Z': 'Europe',
            '1': 'North America', '2': 'North America', '3': 'North America', '4': 'North America', '5': 'North America',
            '6': 'Oceania', '7': 'Oceania',
            '8': 'South America', '9': 'South America'
        }

    def validate_vin(self, vin: str) -> Dict[str, Any]:
        """
        Comprehensive VIN validation with API fallback
        
        Args:
            vin (str): Vehicle Identification Number to validate
            
        Returns:
            Dict[str, Any]: Validation results with detailed information
            
        Raises:
            ValueError: If input is not a string
        """
        if not isinstance(vin, str):
            raise ValueError("VIN must be a string")

        result = {
            'is_valid': False,
            'errors': [],
            'details': {
                'wmi': None,
                'region': None,
                'country': None,
                'manufacturer': None,
                'year': None,
                'check_digit_valid': False,
                'api_source': None
            }
        }

        if not self._validate_basic(vin, result):
            return result

        vin = vin.upper()

        # Try APIs first
        primary_result = self._try_primary_api(vin)
        if primary_result.get('success'):
            result.update(primary_result['data'])
            result['details']['api_source'] = 'primary'
            return result

        secondary_result = self._try_secondary_api(vin)
        if secondary_result.get('success'):
            result.update(secondary_result['data'])
            result['details']['api_source'] = 'secondary'
            return result

        # Add model decoding after manufacturer validation
        self._validate_manufacturer(vin, result)
        self._decode_model(vin, result)
        self._validate_check_digit(vin, result)
        self._validate_year(vin, result)
        result['details']['api_source'] = 'manual'
        
        result['is_valid'] = len(result['errors']) == 0
        return result

    def _validate_basic(self, vin: str, result: dict) -> bool:
        """Basic VIN validation checks"""
        if not vin:
            result['errors'].append("VIN cannot be empty")
            return False
            
        if not isinstance(vin, str):
            result['errors'].append("VIN must be a string")
            return False

        if len(vin) != self.VIN_LENGTH:
            result['errors'].append(f"VIN must be {self.VIN_LENGTH} characters long")
            return False

        vin = vin.upper()
        invalid_chars = set(vin) - self.valid_chars
        if invalid_chars:
            result['errors'].append(f"Invalid characters in VIN: {', '.join(invalid_chars)}")
            return False

        return True

    def _try_primary_api(self, vin: str) -> dict:
        """Try to validate VIN using primary API with retries"""
        if vin in self._cache:
            return self._cache[vin]

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{self.primary_api_url}{vin}?format=json",
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('Results'):
                        result = {
                            'success': True,
                            'data': {
                                'is_valid': True,
                                'details': {
                                    'year': data['Results'][0].get('ModelYear'),
                                    'manufacturer': data['Results'][0].get('Manufacturer'),
                                    'make': data['Results'][0].get('Make'),
                                    'model': data['Results'][0].get('Model'),
                                    'vehicle_type': data['Results'][0].get('VehicleType'),
                                    'check_digit_valid': True
                                }
                            }
                        }
                        self._cache[vin] = result
                        return result
                
                # Handle rate limiting
                if response.status_code == 429:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {'success': False, 'error': str(e)}
                time.sleep(1)
                
        return {'success': False, 'error': 'Max retries exceeded'}

    def _try_secondary_api(self, vin: str) -> dict:
        """
        Try to validate VIN using APIVerve VIN decoder API
        """
        try:
            # Prepare the query as shown in documentation
            query = {"vin": vin}
            
            # Make API request
            response = requests.get(
                self.secondary_api_url,
                params=query,
                headers={
                    'Authorization': f'Bearer {self.apiverve_key}'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok' and data.get('data'):
                    vehicle_data = data['data']
                    return {
                        'success': True,
                        'data': {
                            'is_valid': True,
                            'details': {
                                'year': vehicle_data.get('year'),
                                'make': vehicle_data.get('make'),
                                'manufacturer': vehicle_data.get('manufacturer'),
                                'model': vehicle_data.get('model'),
                                'vehicle_type': vehicle_data.get('vehicletype'),
                                'trim': vehicle_data.get('trim'),
                                'transmission': {
                                    'style': vehicle_data.get('transmissionstyle'),
                                    'speeds': vehicle_data.get('transmissionspeeds')
                                },
                                'engine': {
                                    'type': vehicle_data.get('valvetraindesign'),
                                    'configuration': vehicle_data.get('engineconfiguration')
                                },
                                'check_digit_valid': True
                            }
                        }
            
            return {
                'success': False,
                'error': f'API request failed with status code: {response.status_code}'
            }
            
        except requests.RequestException as e:
            print(f"Secondary API error: {str(e)}")
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except (KeyError, ValueError) as e:
            print(f"Secondary API data parsing error: {str(e)}")
            return {
                'success': False,
                'error': f'Error parsing API response: {str(e)}'
            }

    def _get_year_from_code(self, year_code: str) -> Optional[int]:
        """Calculate the actual year from the VIN year code using a rolling 30-year window."""
        if year_code not in self.year_map:
            return None

        try:
            current_year = datetime.now().year
            position_in_cycle = self.year_map[year_code]
            
            base_year = current_year - 15  # Center of the window
            base_year = base_year - ((base_year % 30))  # Round down to start of cycle
            
            calculated_year = base_year + position_in_cycle - 1
            
            # If the calculated year is too far in the future, 
            # it belongs to the previous cycle
            if calculated_year > current_year + 15:
                calculated_year -= 30
                
            return calculated_year
            
        except Exception as e:
            print(f"Error calculating year: {str(e)}")
            return None

    def _validate_year(self, vin: str, result: dict) -> None:
        """Validate model year code (10th position)"""
        year_code = vin[9]
        calculated_year = self._get_year_from_code(year_code)
        
        if calculated_year:
            result['details']['year'] = calculated_year
        else:
            result['errors'].append(f"Invalid year code: {year_code}")

    def _validate_manufacturer(self, vin: str, result: dict) -> None:
        """Validate manufacturer based on WMI (first 3 characters)"""
        wmi = vin[:3]
        wmi_2 = vin[:2]  # Some manufacturers use 2 characters
        
        # Should add length check before slicing
        if len(vin) < 3:
            result['errors'].append("VIN too short for WMI validation")
            return
        
        if wmi in self.wmi_map:
            info = self.wmi_map[wmi]
            result['details'].update({
                'manufacturer': info['manufacturer'],
                'country': info['country'],
                'region': info['region'],
                'wmi': wmi
            })
        elif wmi_2 in self.wmi_map:
            info = self.wmi_map[wmi_2]
            result['details'].update({
                'manufacturer': info['manufacturer'],
                'country': info['country'],
                'region': info['region'],
                'wmi': wmi_2
            })
        else:
            result['errors'].append(f"Unknown manufacturer WMI: {wmi}")
            # Still include the WMI in the details
            result['details']['wmi'] = wmi

    def _validate_check_digit(self, vin: str, result: dict) -> None:
        """Validate VIN check digit (9th position)"""
        try:
            check_sum = 0
            for i in range(17):
                check_sum += self.transliteration[vin[i]] * self.weights[i]
            
            check_digit = check_sum % 11
            check_digit = 'X' if check_digit == 10 else str(check_digit)
            
            if check_digit == vin[8]:
                result['details']['check_digit_valid'] = True
            else:
                result['errors'].append("Invalid check digit")
        except KeyError:
            result['errors'].append("Unable to calculate check digit")

    def _decode_model(self, vin: str, result: dict) -> None:
        """Attempt to decode vehicle model from VDS"""
        wmi = vin[:3]
        wmi_2 = vin[:2]

        try:
            if wmi in self.vds_patterns:
                patterns = self.vds_patterns[wmi]
                if 'model_codes' in patterns:
                    model_code = vin[3:5]  # Most manufacturers use positions 4-5
                    if model_code in patterns['model_codes']:
                        result['details']['model'] = patterns['model_codes'][model_code]
                    else:
                        result['details']['model'] = 'Unknown model code'
            elif wmi_2 in self.vds_patterns:
                patterns = self.vds_patterns[wmi_2]
                if 'model_codes' in patterns:
                    model_code = vin[3]  # Some manufacturers use just position 4
                    if model_code in patterns['model_codes']:
                        result['details']['model'] = patterns['model_codes'][model_code]
                    else:
                        result['details']['model'] = 'Unknown model code'
        except Exception as e:
            result['details']['model'] = 'Unable to decode model'
            result['errors'].append(f"Model decoding error: {str(e)}")


if __name__ == "__main__":
    validator = VINValidator()
    
    test_vins = [
        "1HGCM82633A123456",  # Sample Honda VIN
        "WVWZZZ1JZ3W386752",  # Sample Volkswagen VIN
        "JH4DA9370MS001234",  # Sample Acura VIN
    ]
    
    for vin in test_vins:
        result = validator.validate_vin(vin)
        print(f"\nVIN: {vin}")
        print(f"Valid: {result['is_valid']}")
        print(f"API Source: {result['details']['api_source']}")
        if result['errors']:
            print("Errors:", result['errors'])
        if result['details']:
            print("Details:", result['details'])