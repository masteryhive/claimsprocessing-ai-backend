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

        self.primary_api_url = "https://https://vpic.nhtsa.dot.gov/decoder/"
        self.secondary_api_url = "https://api.apiverve.com/v1/vindecoder"
        self.apiverve_key = "69e59d74-3843-4ec7-bcf6-e68d4e01b346"  # Replace with your actual APIVerve API key

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
            'status': 'error',
            'manufacturer': None,
            'model_year': None,
            'make': None,
            'model': None,
            'errors': []
        }

        if not self._validate_basic(vin, result):
            return result

        vin = vin.upper()

        # Try APIs first
        primary_result = self._try_primary_api(vin)
        if primary_result.get('success'):
            result.update({
                'status': 'success',
                'manufacturer': primary_result['data']['manufacturer'],
                'model_year': primary_result['data']['year'],
                'make': primary_result['data']['make'],
                'model': primary_result['data']['model']
            })
            return result

        secondary_result = self._try_secondary_api(vin)
        if secondary_result.get('success'):
            result.update({
                'status': 'success',
                'manufacturer': secondary_result['data']['manufacturer'],
                'model_year': secondary_result['data']['year'],
                'make': secondary_result['data']['make'],
                'model': secondary_result['data']['model']
            })
            return result

        # Add model decoding after manufacturer validation
        self._validate_manufacturer(vin, result)
        self._decode_model(vin, result)
        self._validate_year(vin, result)

        # Check if we have valid data to update the result
        if result['manufacturer']:
            result['status'] = 'success'

        return result

    def _validate_basic(self, vin: str, result: dict) -> bool:
        """Basic VIN validation checks"""
        if not vin:
            result['errors'].append("VIN cannot be empty")
            return False
            
        if not isinstance(vin, str):
            result['errors'].append("VIN must be a string")
            return False

        if len(vin) != 17:
            result['errors'].append(f"VIN must be 17 characters long")
            return False

        vin = vin.upper()
        invalid_chars = set(vin) - self.valid_chars
        if invalid_chars:
            result['errors'].append(f"Invalid characters in VIN: {', '.join(invalid_chars)}")
            return False

        return True

    def _try_primary_api(self, vin: str) -> dict:
        """Try to validate VIN using the NHTSA API"""
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get('Results'):
                # Initialize variables to hold the extracted values
                manufacturer = None
                model_year = None
                make = None
                model = None
                
                # Iterate through the results to find the relevant information
                for item in data['Results']:
                    if item['Variable'] == 'Manufacturer Name':
                        manufacturer = item['Value']
                    elif item['Variable'] == 'Model Year':
                        model_year = item['Value']
                    elif item['Variable'] == 'Make':
                        make = item['Value']
                    elif item['Variable'] == 'Model':
                        model = item['Value']

                return {
                    'success': True,
                    'data': {
                        'manufacturer': manufacturer if manufacturer else 'N/A',
                        'year': model_year if model_year else 'N/A',
                        'make': make if make else 'N/A',
                        'model': model if model else 'N/A'
                    }
                }
        return {'success': False}

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
                            'manufacturer': vehicle_data.get('manufacturer'),
                            'year': vehicle_data.get('year'),
                            'make': vehicle_data.get('make'),
                            'model': vehicle_data.get('model')
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
            base_year = self.year_map[year_code]
            current_year = datetime.now().year
            
            # Compute the closest valid VIN cycle using modulo
            cycle_offset = ((current_year - base_year) // 30) * 30
            adjusted_year = base_year + cycle_offset

            # Ensure it's within the valid rolling window (current year ± 15)
            if adjusted_year > current_year + 15:
                adjusted_year -= 30  # Shift back one cycle

            return adjusted_year
        
        except Exception as e:
            print(f"Error calculating year: {str(e)}")
            return None

    def _validate_year(self, vin: str, result: dict) -> None:
        """Validate model year code (10th position)"""
        year_code = vin[9]
        calculated_year = self._get_year_from_code(year_code)
        
        if calculated_year:
            result['model_year'] = calculated_year
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
            result['manufacturer'] = info['manufacturer']
        elif wmi_2 in self.wmi_map:
            info = self.wmi_map[wmi_2]
            result['manufacturer'] = info['manufacturer']
        else:
            result['errors'].append(f"Unknown manufacturer WMI: {wmi}")
            # Still include the WMI in the details
            result['manufacturer'] = wmi

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
                        result['model'] = patterns['model_codes'][model_code]
                    else:
                        result['model'] = 'Unknown model code'
            elif wmi_2 in self.vds_patterns:
                patterns = self.vds_patterns[wmi_2]
                if 'model_codes' in patterns:
                    model_code = vin[3]  # Some manufacturers use just position 4
                    if model_code in patterns['model_codes']:
                        result['model'] = patterns['model_codes'][model_code]
                    else:
                        result['model'] = 'Unknown model code'
        except Exception as e:
            result['model'] = 'Unable to decode model'
            result['errors'].append(f"Model decoding error: {str(e)}")


if __name__ == "__main__":
    validator = VINValidator()
    
    # Test a single VIN
    vin = "KMHJN81PB9u948267"  # Sample Honda VIN
    result = validator.validate_vin(vin)
    print(f"\nVIN: {vin}")
    print(f"Valid: {result['status'] == 'success'}")
    if result['errors']:
        print("Errors:", result['errors'])
    if result['manufacturer']:
        print("Manufacturer:", result['manufacturer'])
    if result['model_year']:
        print("Model Year:", result['model_year'])
    if result['make']:
        print("Make:", result['make'])
    if result['model']:
        print("Model:", result['model'])

 