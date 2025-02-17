"""
VIN data mappings for manufacturer codes and model patterns
"""

from typing import Dict, Any

# World Manufacturer Identifier (WMI) mappings
WMI_MAP: Dict[str, Dict[str, str]] = {
            # North America - United States (1,4,5)
            '1FA': {'manufacturer': 'Ford Motor Company', 'country': 'United States', 'region': 'North America'},
            '1FB': {'manufacturer': 'Ford Motor Company (Bus)', 'country': 'United States', 'region': 'North America'},
            '1FC': {'manufacturer': 'Ford Motor Company (Commercial trucks)', 'country': 'United States', 'region': 'North America'},
            '1FT': {'manufacturer': 'Ford Motor Company (MPV)', 'country': 'United States', 'region': 'North America'},
            '1G': {'manufacturer': 'General Motors', 'country': 'United States', 'region': 'North America'},
            '1GA': {'manufacturer': 'General Motors', 'country': 'United States', 'region': 'North America'},
            '1GC': {'manufacturer': 'Chevrolet Truck', 'country': 'United States', 'region': 'North America'},
            '1GM': {'manufacturer': 'Pontiac', 'country': 'United States', 'region': 'North America'},
            '1H': {'manufacturer': 'Honda', 'country': 'United States', 'region': 'North America'},
            '1HD': {'manufacturer': 'Harley-Davidson', 'country': 'United States', 'region': 'North America'},
            '1J4': {'manufacturer': 'Jeep', 'country': 'United States', 'region': 'North America'},
            '1L': {'manufacturer': 'Lincoln', 'country': 'United States', 'region': 'North America'},
            '1M': {'manufacturer': 'Mercury', 'country': 'United States', 'region': 'North America'},
            '1N': {'manufacturer': 'Nissan', 'country': 'United States', 'region': 'North America'},
            '1VW': {'manufacturer': 'Volkswagen', 'country': 'United States', 'region': 'North America'},
            
            # Canada (2)
            '2B': {'manufacturer': 'Bombardier', 'country': 'Canada', 'region': 'North America'},
            '2C': {'manufacturer': 'Chrysler Canada', 'country': 'Canada', 'region': 'North America'},
            '2FA': {'manufacturer': 'Ford Motor Company', 'country': 'Canada', 'region': 'North America'},
            '2G': {'manufacturer': 'General Motors', 'country': 'Canada', 'region': 'North America'},
            '2HG': {'manufacturer': 'Honda', 'country': 'Canada', 'region': 'North America'},
            '2T': {'manufacturer': 'Toyota', 'country': 'Canada', 'region': 'North America'},
            
            # Mexico (3)
            '3G': {'manufacturer': 'General Motors Mexico', 'country': 'Mexico', 'region': 'North America'},
            '3H': {'manufacturer': 'Honda Mexico', 'country': 'Mexico', 'region': 'North America'},
            '3N': {'manufacturer': 'Nissan Mexico', 'country': 'Mexico', 'region': 'North America'},
            '3VW': {'manufacturer': 'Volkswagen Mexico', 'country': 'Mexico', 'region': 'North America'},
            
            # Japan (J)
            'JA': {'manufacturer': 'Isuzu', 'country': 'Japan', 'region': 'Asia'},
            'JF': {'manufacturer': 'Fuji Heavy Industries (Subaru)', 'country': 'Japan', 'region': 'Asia'},
            'JH': {'manufacturer': 'Honda', 'country': 'Japan', 'region': 'Asia'},
            'JM': {'manufacturer': 'Mazda', 'country': 'Japan', 'region': 'Asia'},
            'JN': {'manufacturer': 'Nissan', 'country': 'Japan', 'region': 'Asia'},
            'JS': {'manufacturer': 'Suzuki', 'country': 'Japan', 'region': 'Asia'},
            'JT': {'manufacturer': 'Toyota', 'country': 'Japan', 'region': 'Asia'},
            'JY': {'manufacturer': 'Yamaha', 'country': 'Japan', 'region': 'Asia'},
            
            # South Korea (K)
            'KL': {'manufacturer': 'Daewoo', 'country': 'South Korea', 'region': 'Asia'},
            'KM': {'manufacturer': 'Hyundai', 'country': 'South Korea', 'region': 'Asia'},
            'KN': {'manufacturer': 'Kia', 'country': 'South Korea', 'region': 'Asia'},
            
            # China (L)
            'LB': {'manufacturer': 'BYD', 'country': 'China', 'region': 'Asia'},
            'LFB': {'manufacturer': 'FAW', 'country': 'China', 'region': 'Asia'},
            'LGX': {'manufacturer': 'BYD', 'country': 'China', 'region': 'Asia'},
            'LRX': {'manufacturer': 'Great Wall', 'country': 'China', 'region': 'Asia'},
            'LSG': {'manufacturer': 'SAIC General Motors', 'country': 'China', 'region': 'Asia'},
            'LZW': {'manufacturer': 'SAIC-GM-Wuling', 'country': 'China', 'region': 'Asia'},
            
            # Germany (W)
            'WA': {'manufacturer': 'Audi', 'country': 'Germany', 'region': 'Europe'},
            'WBA': {'manufacturer': 'BMW', 'country': 'Germany', 'region': 'Europe'},
            'WBS': {'manufacturer': 'BMW M', 'country': 'Germany', 'region': 'Europe'},
            'WDB': {'manufacturer': 'Mercedes-Benz', 'country': 'Germany', 'region': 'Europe'},
            'WDD': {'manufacturer': 'Mercedes-Benz', 'country': 'Germany', 'region': 'Europe'},
            'WMW': {'manufacturer': 'MINI', 'country': 'Germany', 'region': 'Europe'},
            'WP0': {'manufacturer': 'Porsche', 'country': 'Germany', 'region': 'Europe'},
            'WVW': {'manufacturer': 'Volkswagen', 'country': 'Germany', 'region': 'Europe'},
            
            # Sweden (YV)
            'YV1': {'manufacturer': 'Volvo Cars', 'country': 'Sweden', 'region': 'Europe'},
            'YV2': {'manufacturer': 'Volvo Trucks', 'country': 'Sweden', 'region': 'Europe'},
            'YV3': {'manufacturer': 'Volvo Buses', 'country': 'Sweden', 'region': 'Europe'},
            
            # Italy (ZA)
            'ZAM': {'manufacturer': 'Maserati', 'country': 'Italy', 'region': 'Europe'},
            'ZAR': {'manufacturer': 'Alfa Romeo', 'country': 'Italy', 'region': 'Europe'},
            'ZFA': {'manufacturer': 'Fiat', 'country': 'Italy', 'region': 'Europe'},
            'ZFF': {'manufacturer': 'Ferrari', 'country': 'Italy', 'region': 'Europe'},
            
            # Brazil (9)
            '9BW': {'manufacturer': 'Volkswagen Brazil', 'country': 'Brazil', 'region': 'South America'},
            '93H': {'manufacturer': 'Honda Brazil', 'country': 'Brazil', 'region': 'South America'},
            '93Y': {'manufacturer': 'Renault Brazil', 'country': 'Brazil', 'region': 'South America'},
            '9BG': {'manufacturer': 'General Motors Brazil', 'country': 'Brazil', 'region': 'South America'},
            
            # Additional European Manufacturers
            'SAJ': {'manufacturer': 'Jaguar', 'country': 'United Kingdom', 'region': 'Europe'},
            'SAL': {'manufacturer': 'Land Rover', 'country': 'United Kingdom', 'region': 'Europe'},
            'SCA': {'manufacturer': 'Rolls Royce', 'country': 'United Kingdom', 'region': 'Europe'},
            'SCC': {'manufacturer': 'Lotus Cars', 'country': 'United Kingdom', 'region': 'Europe'},
            'SCF': {'manufacturer': 'Aston Martin', 'country': 'United Kingdom', 'region': 'Europe'},
            'TMA': {'manufacturer': 'Hyundai Motor Manufacturing', 'country': 'Czech Republic', 'region': 'Europe'},
            'TMB': {'manufacturer': 'Škoda', 'country': 'Czech Republic', 'region': 'Europe'},
            'TRU': {'manufacturer': 'Audi Hungary', 'country': 'Hungary', 'region': 'Europe'},
            'UU1': {'manufacturer': 'Dacia', 'country': 'Romania', 'region': 'Europe'},
            'VF1': {'manufacturer': 'Renault', 'country': 'France', 'region': 'Europe'},
            'VF3': {'manufacturer': 'Peugeot', 'country': 'France', 'region': 'Europe'},
            'VF7': {'manufacturer': 'Citroën', 'country': 'France', 'region': 'Europe'},
            'VLV': {'manufacturer': 'Scania', 'country': 'Netherlands', 'region': 'Europe'},
            
            # Additional Asian Manufacturers
            'JHL': {'manufacturer': 'Honda Motorcycle', 'country': 'Japan', 'region': 'Asia'},
            'JK': {'manufacturer': 'Kawasaki', 'country': 'Japan', 'region': 'Asia'},
            'JMB': {'manufacturer': 'Mitsubishi', 'country': 'Japan', 'region': 'Asia'},
            'JTD': {'manufacturer': 'Toyota Daihatsu', 'country': 'Japan', 'region': 'Asia'},
            'KNA': {'manufacturer': 'Kia Motors', 'country': 'South Korea', 'region': 'Asia'},
            'KNB': {'manufacturer': 'Kia Motors', 'country': 'South Korea', 'region': 'Asia'},
            'KPT': {'manufacturer': 'SsangYong', 'country': 'South Korea', 'region': 'Asia'},
            'LBE': {'manufacturer': 'Beijing Hyundai', 'country': 'China', 'region': 'Asia'},
            'LBV': {'manufacturer': 'BMW Brilliance', 'country': 'China', 'region': 'Asia'},
            'LDC': {'manufacturer': 'Dongfeng', 'country': 'China', 'region': 'Asia'},
            'LE4': {'manufacturer': 'Beijing Benz', 'country': 'China', 'region': 'Asia'},
            'LFP': {'manufacturer': 'FAW Toyota', 'country': 'China', 'region': 'Asia'},
            'LFV': {'manufacturer': 'FAW Volkswagen', 'country': 'China', 'region': 'Asia'},
            'LGJ': {'manufacturer': 'Dongfeng Nissan', 'country': 'China', 'region': 'Asia'},
            'LH1': {'manufacturer': 'FAW Haima', 'country': 'China', 'region': 'Asia'},
            'LJD': {'manufacturer': 'JAC', 'country': 'China', 'region': 'Asia'},
            'LLV': {'manufacturer': 'Lifan', 'country': 'China', 'region': 'Asia'},
            'LMG': {'manufacturer': 'GAC', 'country': 'China', 'region': 'Asia'},
            'LPA': {'manufacturer': 'Changan PSA (DS)', 'country': 'China', 'region': 'Asia'},
            'LS5': {'manufacturer': 'Changan Suzuki', 'country': 'China', 'region': 'Asia'},
            'LVG': {'manufacturer': 'Great Wall', 'country': 'China', 'region': 'Asia'},
            'LVH': {'manufacturer': 'Dongfeng Honda', 'country': 'China', 'region': 'Asia'},
            'LVR': {'manufacturer': 'Changan Mazda', 'country': 'China', 'region': 'Asia'},
            'LVS': {'manufacturer': 'Changan Ford', 'country': 'China', 'region': 'Asia'},
            'LVV': {'manufacturer': 'Chery', 'country': 'China', 'region': 'Asia'},
            'LZY': {'manufacturer': 'Yutong', 'country': 'China', 'region': 'Asia'},
            
            # Additional North American Manufacturers
            '1C': {'manufacturer': 'Chrysler', 'country': 'United States', 'region': 'North America'},
            '1F': {'manufacturer': 'Ford', 'country': 'United States', 'region': 'North America'},
            '1GH': {'manufacturer': 'GM Medium Duty Trucks', 'country': 'United States', 'region': 'North America'},
            '1GT': {'manufacturer': 'GMC Truck', 'country': 'United States', 'region': 'North America'},
            '1GY': {'manufacturer': 'Cadillac', 'country': 'United States', 'region': 'North America'},
            '1HG': {'manufacturer': 'Honda USA', 'country': 'United States', 'region': 'North America'},
            '1N4': {'manufacturer': 'Nissan USA', 'country': 'United States', 'region': 'North America'},
            '1NX': {'manufacturer': 'NUMMI (Toyota)', 'country': 'United States', 'region': 'North America'},
            '1TV': {'manufacturer': 'Toyota USA', 'country': 'United States', 'region': 'North America'},
            '2FT': {'manufacturer': 'Ford Truck Canada', 'country': 'Canada', 'region': 'North America'},
            '2M': {'manufacturer': 'Mercury', 'country': 'Canada', 'region': 'North America'},
            '2WK': {'manufacturer': 'Western Star', 'country': 'Canada', 'region': 'North America'},
            '3FE': {'manufacturer': 'Ford Mexico', 'country': 'Mexico', 'region': 'North America'},
            
            # Additional South American Manufacturers
            '8A1': {'manufacturer': 'Renault Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AF': {'manufacturer': 'Ford Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AG': {'manufacturer': 'GM Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AJ': {'manufacturer': 'Toyota Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AK': {'manufacturer': 'Suzuki Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AP': {'manufacturer': 'Fiat Argentina', 'country': 'Argentina', 'region': 'South America'},
            '8AW': {'manufacturer': 'Volkswagen Argentina', 'country': 'Argentina', 'region': 'South America'},
            '93R': {'manufacturer': 'Toyota Brazil', 'country': 'Brazil', 'region': 'South America'},
            '9BR': {'manufacturer': 'Toyota Brazil', 'country': 'Brazil', 'region': 'South America'},
            '9FB': {'manufacturer': 'Ford Brazil', 'country': 'Brazil', 'region': 'South America'},
            
            # Additional Australian/Oceania Manufacturers
            '6F': {'manufacturer': 'Ford Australia', 'country': 'Australia', 'region': 'Oceania'},
            '6G1': {'manufacturer': 'GM Holden', 'country': 'Australia', 'region': 'Oceania'},
            '6MM': {'manufacturer': 'Mitsubishi Motors Australia', 'country': 'Australia', 'region': 'Oceania'},
            '6T1': {'manufacturer': 'Toyota Australia', 'country': 'Australia', 'region': 'Oceania'},
            
            # Additional Indian Manufacturers (R)
            'RLA': {'manufacturer': 'Mahindra & Mahindra', 'country': 'India', 'region': 'Asia'},
            'RLB': {'manufacturer': 'Maruti Suzuki', 'country': 'India', 'region': 'Asia'},
            'RLC': {'manufacturer': 'Tata Motors', 'country': 'India', 'region': 'Asia'},

            # Additional European Manufacturers
            'SB1': {'manufacturer': 'Toyota UK', 'country': 'United Kingdom', 'region': 'Europe'},
            'SDB': {'manufacturer': 'Peugeot UK (Talbot)', 'country': 'United Kingdom', 'region': 'Europe'},
            'SFD': {'manufacturer': 'Alexander Dennis', 'country': 'United Kingdom', 'region': 'Europe'},
            'SHS': {'manufacturer': 'Honda UK', 'country': 'United Kingdom', 'region': 'Europe'},
            'SUD': {'manufacturer': 'Leyland Trucks', 'country': 'United Kingdom', 'region': 'Europe'},
            'TK9': {'manufacturer': 'SOR', 'country': 'Czech Republic', 'region': 'Europe'},
            'TN9': {'manufacturer': 'Karosa', 'country': 'Czech Republic', 'region': 'Europe'},
            'TSM': {'manufacturer': 'Suzuki Hungary', 'country': 'Hungary', 'region': 'Europe'},
            'UNK': {'manufacturer': 'Ikarus Bus', 'country': 'Hungary', 'region': 'Europe'},
            'UU6': {'manufacturer': 'UAZ', 'country': 'Romania', 'region': 'Europe'},
            'UZT': {'manufacturer': 'UzDaewoo', 'country': 'Uzbekistan', 'region': 'Europe'},
            'VF2': {'manufacturer': 'Renault Trucks', 'country': 'France', 'region': 'Europe'},
            'VF4': {'manufacturer': 'Talbot', 'country': 'France', 'region': 'Europe'},
            'VF6': {'manufacturer': 'Renault Trucks/Buses', 'country': 'France', 'region': 'Europe'},
            'VF8': {'manufacturer': 'Matra/Talbot', 'country': 'France', 'region': 'Europe'},
            'VF9': {'manufacturer': 'Bugatti', 'country': 'France', 'region': 'Europe'},
            'VNK': {'manufacturer': 'Toyota France', 'country': 'France', 'region': 'Europe'},
            'VSK': {'manufacturer': 'Nissan Spain', 'country': 'Spain', 'region': 'Europe'},
            'VSS': {'manufacturer': 'SEAT', 'country': 'Spain', 'region': 'Europe'},
            'VSX': {'manufacturer': 'Opel Spain', 'country': 'Spain', 'region': 'Europe'},
            'VV9': {'manufacturer': 'TAURO', 'country': 'Spain', 'region': 'Europe'},
            'VWA': {'manufacturer': 'Nissan Germany', 'country': 'Germany', 'region': 'Europe'},
            'VWV': {'manufacturer': 'Volkswagen Spain', 'country': 'Spain', 'region': 'Europe'},
            'W09': {'manufacturer': 'Ruf Automobile', 'country': 'Germany', 'region': 'Europe'},
            'WAG': {'manufacturer': 'Neoplan', 'country': 'Germany', 'region': 'Europe'},
            'WAU': {'manufacturer': 'Audi', 'country': 'Germany', 'region': 'Europe'},
            'WMA': {'manufacturer': 'MAN', 'country': 'Germany', 'region': 'Europe'},
            'WPO': {'manufacturer': 'Porsche', 'country': 'Germany', 'region': 'Europe'},
            'WSM': {'manufacturer': 'Smart', 'country': 'Germany', 'region': 'Europe'},
            'XLR': {'manufacturer': 'DAF Trucks', 'country': 'Netherlands', 'region': 'Europe'},
            'XTA': {'manufacturer': 'AvtoVAZ', 'country': 'Russia', 'region': 'Europe'},
            'XTB': {'manufacturer': 'AZLK', 'country': 'Russia', 'region': 'Europe'},
            'XW8': {'manufacturer': 'Volkswagen Russia', 'country': 'Russia', 'region': 'Europe'},
            'YBW': {'manufacturer': 'Volkswagen Belgium', 'country': 'Belgium', 'region': 'Europe'},
            'YK1': {'manufacturer': 'Saab', 'country': 'Sweden', 'region': 'Europe'},
            'YS2': {'manufacturer': 'Scania AB', 'country': 'Sweden', 'region': 'Europe'},
            'YS3': {'manufacturer': 'Saab', 'country': 'Sweden', 'region': 'Europe'},
            'YS4': {'manufacturer': 'Scania Bus', 'country': 'Sweden', 'region': 'Europe'},
            'YTN': {'manufacturer': 'Saab NEVS', 'country': 'Sweden', 'region': 'Europe'},
            'ZAP': {'manufacturer': 'Piaggio', 'country': 'Italy', 'region': 'Europe'},
            'ZCF': {'manufacturer': 'Iveco', 'country': 'Italy', 'region': 'Europe'},
            'ZLA': {'manufacturer': 'Lancia', 'country': 'Italy', 'region': 'Europe'},

            # Additional Asian Manufacturers
            'JL5': {'manufacturer': 'Mitsubishi Fuso', 'country': 'Japan', 'region': 'Asia'},
            'JMY': {'manufacturer': 'Mitsubishi Motors', 'country': 'Japan', 'region': 'Asia'},
            'JNK': {'manufacturer': 'Nissan Diesel', 'country': 'Japan', 'region': 'Asia'},
            'JSK': {'manufacturer': 'Suzuki', 'country': 'Japan', 'region': 'Asia'},
            'KL1': {'manufacturer': 'GM Korea', 'country': 'South Korea', 'region': 'Asia'},
            'KMH': {'manufacturer': 'Hyundai', 'country': 'South Korea', 'region': 'Asia'},
            'KNJ': {'manufacturer': 'Kia', 'country': 'South Korea', 'region': 'Asia'},
            'LAE': {'manufacturer': 'Jiangxi Jiangling', 'country': 'China', 'region': 'Asia'},
            'LC0': {'manufacturer': 'BYD Auto', 'country': 'China', 'region': 'Asia'},
            'LFM': {'manufacturer': 'FAW Car', 'country': 'China', 'region': 'Asia'},
            'LGH': {'manufacturer': 'Guangzhou Honda', 'country': 'China', 'region': 'Asia'},
            'LGW': {'manufacturer': 'Great Wall', 'country': 'China', 'region': 'Asia'},
            'LJ1': {'manufacturer': 'JAC', 'country': 'China', 'region': 'Asia'},
            'LKL': {'manufacturer': 'Suzhou King Long', 'country': 'China', 'region': 'Asia'},
            'LSY': {'manufacturer': 'Brilliance', 'country': 'China', 'region': 'Asia'},
            'LTV': {'manufacturer': 'FAW Toyota', 'country': 'China', 'region': 'Asia'},
            'LVS': {'manufacturer': 'Changan Ford', 'country': 'China', 'region': 'Asia'},
            'LZM': {'manufacturer': 'MAN China', 'country': 'China', 'region': 'Asia'},
            'MHR': {'manufacturer': 'Honda Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'MLC': {'manufacturer': 'Suzuki Motor Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'MMB': {'manufacturer': 'Mitsubishi Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'MNB': {'manufacturer': 'Nissan Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'MNT': {'manufacturer': 'Nissan Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'MPB': {'manufacturer': 'Toyota Thailand', 'country': 'Thailand', 'region': 'Asia'},
            'NLA': {'manufacturer': 'Honda Cars India', 'country': 'India', 'region': 'Asia'},
            'NMB': {'manufacturer': 'Maruti Suzuki', 'country': 'India', 'region': 'Asia'},
            'PE1': {'manufacturer': 'Ford Philippines', 'country': 'Philippines', 'region': 'Asia'},
            'PL1': {'manufacturer': 'Proton', 'country': 'Malaysia', 'region': 'Asia'},

            # Additional North American Manufacturers
            '1G1': {'manufacturer': 'Chevrolet USA', 'country': 'United States', 'region': 'North America'},
            '1G2': {'manufacturer': 'Pontiac', 'country': 'United States', 'region': 'North America'},
            '1G3': {'manufacturer': 'Oldsmobile', 'country': 'United States', 'region': 'North America'},
            '1G4': {'manufacturer': 'Buick', 'country': 'United States', 'region': 'North America'},
            '1G6': {'manufacturer': 'Cadillac', 'country': 'United States', 'region': 'North America'},
            '1GK': {'manufacturer': 'GMC', 'country': 'United States', 'region': 'North America'},
            '1H': {'manufacturer': 'Honda USA', 'country': 'United States', 'region': 'North America'},
            '1J8': {'manufacturer': 'Jeep', 'country': 'United States', 'region': 'North America'},
            '1ME': {'manufacturer': 'Mercury', 'country': 'United States', 'region': 'North America'},
            '1N6': {'manufacturer': 'Nissan USA', 'country': 'United States', 'region': 'North America'},
            '1XK': {'manufacturer': 'Kenworth', 'country': 'United States', 'region': 'North America'},
            '1XP': {'manufacturer': 'Peterbilt', 'country': 'United States', 'region': 'North America'},
            '2CN': {'manufacturer': 'CAMI', 'country': 'Canada', 'region': 'North America'},
            '2D3': {'manufacturer': 'Dodge Canada', 'country': 'Canada', 'region': 'North America'},
            '2GC': {'manufacturer': 'GM Canada', 'country': 'Canada', 'region': 'North America'},
            '3D3': {'manufacturer': 'Dodge Mexico', 'country': 'Mexico', 'region': 'North America'},
            '3GC': {'manufacturer': 'GM Mexico', 'country': 'Mexico', 'region': 'North America'},

            # Additional South American Manufacturers
            '8GG': {'manufacturer': 'Chevrolet Chile', 'country': 'Chile', 'region': 'South America'},
            '8GD': {'manufacturer': 'Peugeot Chile', 'country': 'Chile', 'region': 'South America'},
            '935': {'manufacturer': 'Citroën Brazil', 'country': 'Brazil', 'region': 'South America'},
            '936': {'manufacturer': 'Peugeot Brazil', 'country': 'Brazil', 'region': 'South America'},
            '93U': {'manufacturer': 'Audi Brazil', 'country': 'Brazil', 'region': 'South America'},
            '93X': {'manufacturer': 'Mitsubishi Brazil', 'country': 'Brazil', 'region': 'South America'},
            '94D': {'manufacturer': 'Nissan Brazil', 'country': 'Brazil', 'region': 'South America'},
            '988': {'manufacturer': 'Jeep Brazil', 'country': 'Brazil', 'region': 'South America'},
            '98R': {'manufacturer': 'FCA Brazil', 'country': 'Brazil', 'region': 'South America'},
            '9BD': {'manufacturer': 'Fiat Brazil', 'country': 'Brazil', 'region': 'South America'},
            '9BF': {'manufacturer': 'Ford Brazil', 'country': 'Brazil', 'region': 'South America'},

            # Additional Australian/Oceania Manufacturers
            '6U9': {'manufacturer': 'Kenworth Australia', 'country': 'Australia', 'region': 'Oceania'},
            '6U1': {'manufacturer': 'Volvo Australia', 'country': 'Australia', 'region': 'Oceania'},
            '7A1': {'manufacturer': 'Toyota New Zealand', 'country': 'New Zealand', 'region': 'Oceania'},
            '7A3': {'manufacturer': 'Honda New Zealand', 'country': 'New Zealand', 'region': 'Oceania'},

            # Additional African Manufacturers
            'AAV': {'manufacturer': 'Volkswagen South Africa', 'country': 'South Africa', 'region': 'Africa'},
            'AC5': {'manufacturer': 'Ford South Africa', 'country': 'South Africa', 'region': 'Africa'},
            'ADB': {'manufacturer': 'GM South Africa', 'country': 'South Africa', 'region': 'Africa'},
            'AFA': {'manufacturer': 'Ford South Africa', 'country': 'South Africa', 'region': 'Africa'},
            'AHT': {'manufacturer': 'Toyota South Africa', 'country': 'South Africa', 'region': 'Africa'},
        }

# Vehicle Descriptor Section (VDS) patterns
VDS_PATTERNS: Dict[str, Dict[str, Dict[str, str]]] = {
            # Toyota/Lexus (JT, JH)
            'JT': {
                'model_codes': {
                    'BA': 'RAV4',
                    'BF': 'Camry',
                    'BH': 'Prius',
                    'BK': 'Avalon',
                    'BZ': 'Corolla',
                    'CA': 'Sienna',
                    'CK': 'Tundra',
                    'DK': 'Tacoma',
                    'HF': 'Highlander',
                    'JZ': 'Supra',
                    'KU': 'Land Cruiser',
                    'MZ': 'GR86',
                    'NF': 'Venza',
                    'PA': '4Runner',
                    'ZK': 'Sequoia'
                }
            },
            # Lexus specific
            'JTH': {
                'model_codes': {
                    'BA': 'IS',
                    'BF': 'GS',
                    'BH': 'ES',
                    'BK': 'LS',
                    'CA': 'RX',
                    'CK': 'GX',
                    'DK': 'LX',
                    'KD': 'NX',
                    'KZ': 'RC',
                    'LZ': 'LC'
                }
            },
            # Honda/Acura (JH)
            'JH': {
                'model_codes': {
                    'CM': 'Accord',
                    'GK': 'Fit',
                    'RM': 'CR-V',
                    'RU': 'Pilot',
                    'TF': 'Odyssey',
                    'RE': 'HR-V',
                    'KC': 'Civic',
                    'KA': 'Ridgeline',
                    'LB': 'Element',
                    'MC': 'Insight',
                    'PA': 'Passport'
                }
            },
            # Acura specific
            'JHN': {
                'model_codes': {
                    'AE': 'ILX',
                    'KC': 'TLX',
                    'TB': 'MDX',
                    'TC': 'RDX',
                    'DE': 'NSX'
                }
            },
            # BMW (WBA, WBS)
            'WBA': {
                'model_codes': {
                    'A': '1 Series',
                    'B': '2 Series',
                    'C': '3 Series',
                    'D': '4 Series',
                    'E': '5 Series',
                    'F': '6 Series',
                    'G': '7 Series',
                    'H': '8 Series',
                    'K': 'X1',
                    'L': 'X2',
                    'M': 'X3',
                    'N': 'X4',
                    'P': 'X5',
                    'R': 'X6',
                    'S': 'X7',
                    'T': 'Z4',
                    'U': 'i3',
                    'V': 'i8'
                }
            },
            # Mercedes-Benz (WDB, WDD)
            'WDB': {
                'model_codes': {
                    'A': 'A-Class',
                    'B': 'B-Class',
                    'C': 'C-Class',
                    'E': 'E-Class',
                    'S': 'S-Class',
                    'G': 'G-Class',
                    'M': 'M-Class/GLE',
                    'R': 'R-Class',
                    'X': 'X-Class',
                    'V': 'V-Class',
                    'L': 'SL-Class',
                    'K': 'SLK/SLC-Class',
                    'H': 'AMG GT',
                    'N': 'CLA-Class',
                    'P': 'GLA-Class',
                    'Q': 'GLC-Class',
                    'T': 'GLB-Class'
                }
            },
            # Volkswagen (WVW, 3VW)
            'WVW': {
                'model_codes': {
                    'AA': 'Golf/GTI',
                    'AB': 'Passat',
                    'AC': 'Jetta',
                    'AE': 'Tiguan',
                    'AF': 'Touareg',
                    'AG': 'Atlas',
                    'BA': 'Beetle',
                    'CA': 'Arteon',
                    'CV': 'ID.4',
                    'DM': 'Taos'
                }
            },
            # Ford (1FA, 1FM, 1FT)
            '1FA': {
                'model_codes': {
                    'P': 'Mustang',
                    'H': 'Fusion',
                    'K': 'Focus',
                    'D': 'Edge',
                    'E': 'Escape',
                    'R': 'Taurus'
                }
            },
            '1FT': {
                'model_codes': {
                    'W': 'F-150',
                    'X': 'F-250',
                    'Y': 'F-350',
                    'Z': 'F-450',
                    'R': 'Ranger',
                    'E': 'Expedition'
                }
            },
            # Chevrolet (1GC)
            '1GC': {
                'model_codes': {
                    'RC': 'Silverado',
                    'NC': 'Colorado',
                    'PK': 'Suburban',
                    'SK': 'Tahoe',
                    'EC': 'Express'
                }
            },
            # Nissan (JN)
            'JN1': {
                'model_codes': {
                    'AZ': 'Maxima',
                    'BV': 'GT-R',
                    'DA': 'Frontier',
                    'EV': 'LEAF',
                    'MS': 'Rogue',
                    'PB': 'Altima'
                }
            },
            # Audi (WAU)
            'WAU': {
                'model_codes': {
                    'A': 'A3',
                    'B': 'A4',
                    'C': 'A5',
                    'D': 'A6',
                    'E': 'A7',
                    'F': 'A8',
                    'G': 'Q3',
                    'H': 'Q5',
                    'J': 'Q7',
                    'K': 'Q8',
                    'L': 'TT',
                    'M': 'R8'
                }
            },
            # Hyundai (KMH)
            'KMH': {
                'model_codes': {
                    'CN': 'Accent',
                    'DN': 'Elantra',
                    'FN': 'Sonata',
                    'HN': 'Tucson',
                    'JN': 'Santa Fe',
                    'LN': 'Palisade',
                    'MN': 'Veloster',
                    'PN': 'Kona'
                }
            },
            # Kia (KNA)
            'KNA': {
                'model_codes': {
                    'F': 'Forte',
                    'J': 'Optima/K5',
                    'M': 'Stinger',
                    'N': 'Sportage',
                    'P': 'Sorento',
                    'R': 'Telluride',
                    'S': 'Soul',
                    'T': 'Seltos'
                }
            },
            # Subaru (JF)
            'JF1': {
                'model_codes': {
                    'GP': 'Impreza',
                    'VA': 'WRX',
                    'BP': 'Legacy',
                    'BR': 'Outback',
                    'SK': 'Forester',
                    'GN': 'Crosstrek',
                    'KC': 'Ascent',
                    'BN': 'BRZ'
                }
            },
            # Mazda (JM)
            'JM1': {
                'model_codes': {
                    'BL': 'Mazda3',
                    'GJ': 'Mazda6',
                    'KE': 'CX-3',
                    'KF': 'CX-30',
                    'KL': 'CX-5',
                    'KM': 'CX-9',
                    'ND': 'MX-5 Miata'
                }
            },
            # Porsche (WP0, WP1)
            'WP0': {
                'model_codes': {
                    'A': '911',
                    'B': 'Boxster',
                    'C': 'Cayman',
                    'D': 'Taycan'
                }
            },
            'WP1': {
                'model_codes': {
                    'A': 'Cayenne',
                    'B': 'Macan',
                    'C': 'Panamera'
                }
            },
            # Volvo (YV)
            'YV1': {
                'model_codes': {
                    'LZ': 'S60',
                    'MZ': 'S80',
                    'RS': 'XC90',
                    'RZ': 'XC60',
                    'LF': 'V60',
                    'LM': 'V70',
                    'LY': 'S40',
                    'MW': 'C70',
                    'FW': 'V40',
                    'KS': 'XC40'
                }
            },
            # Jaguar (SAJ)
            'SAJ': {
                'model_codes': {
                    'DA': 'XE',
                    'FA': 'XF',
                    'GA': 'XJ',
                    'KA': 'F-TYPE',
                    'PA': 'F-PACE',
                    'EA': 'E-PACE',
                    'VA': 'I-PACE'
                }
            },
            # Land Rover (SAL)
            'SAL': {
                'model_codes': {
                    'MA': 'Range Rover',
                    'WA': 'Range Rover Sport',
                    'HA': 'Range Rover Evoque',
                    'FA': 'Discovery',
                    'BA': 'Discovery Sport',
                    'NA': 'Defender'
                }
            },
            # Infiniti (JN)
            'JN8': {
                'model_codes': {
                    'AR': 'QX80',
                    'MS': 'QX60',
                    'BS': 'QX50',
                    'CS': 'QX30',
                    'FS': 'QX70',
                    'JS': 'QX56'
                }
            },
            # Mitsubishi (JA)
            'JA4': {
                'model_codes': {
                    'AZ': 'Outlander',
                    'BZ': 'Eclipse Cross',
                    'AP': 'Outlander Sport/RVR',
                    'AD': 'Lancer',
                    'AA': 'Mirage'
                }
            },
            # Genesis (KMH)
            'KMR': {
                'model_codes': {
                    'GA': 'G70',
                    'GB': 'G80',
                    'GC': 'G90',
                    'GV': 'GV80',
                    'GW': 'GV70'
                }
            },
            # Cadillac (1G6)
            '1G6': {
                'model_codes': {
                    'DC': 'CT4',
                    'DL': 'CT5',
                    'KY': 'CT6',
                    'LS': 'Escalade',
                    'RX': 'XT4',
                    'RY': 'XT5',
                    'RZ': 'XT6'
                }
            },
            # Buick (1G4)
            '1G4': {
                'model_codes': {
                    'PR': 'Regal',
                    'PS': 'LaCrosse',
                    'PW': 'Enclave',
                    'PX': 'Encore',
                    'PY': 'Envision'
                }
            },
            # GMC (1GT)
            '1GT': {
                'model_codes': {
                    'RC': 'Sierra',
                    'SK': 'Yukon',
                    'TK': 'Canyon',
                    'WK': 'Acadia',
                    'LK': 'Terrain'
                }
            },
            # Dodge (2C3)
            '2C3': {
                'model_codes': {
                    'CD': 'Challenger',
                    'CX': 'Charger',
                    'LD': 'Durango',
                    'RK': 'Ram',
                    'JH': 'Journey'
                }
            },
            # Chrysler (2C4)
            '2C4': {
                'model_codes': {
                    'RC': 'Pacifica',
                    'RN': 'Town & Country',
                    'RR': '300'
                }
            },
            # Jeep (1C4)
            '1C4': {
                'model_codes': {
                    'PJ': 'Cherokee',
                    'RJ': 'Grand Cherokee',
                    'HJ': 'Renegade',
                    'GJ': 'Compass',
                    'DJ': 'Wrangler',
                    'HM': 'Wagoneer'
                }
            },
            # RAM (3C6)
            '3C6': {
                'model_codes': {
                    'RR': '1500',
                    'TR': '2500',
                    'UR': '3500',
                    'MR': 'ProMaster'
                }
            },
            # Maserati (ZAM)
            'ZAM': {
                'model_codes': {
                    'LA': 'Ghibli',
                    'MA': 'Quattroporte',
                    'NA': 'Levante',
                    'PA': 'MC20',
                    'RA': 'Grecale'
                }
            },
            # Alfa Romeo (ZAR)
            'ZAR': {
                'model_codes': {
                    'FA': 'Giulia',
                    'GA': 'Stelvio',
                    'HA': 'Tonale'
                }
            },
            # Ferrari (ZFF)
            'ZFF': {
                'model_codes': {
                    'F2': 'F8 Tributo',
                    'F8': '488',
                    'R7': 'Roma',
                    'N7': 'SF90',
                    'L5': '812',
                    'P4': 'Portofino'
                }
            },
            # Lamborghini (ZHW)
            'ZHW': {
                'model_codes': {
                    'LA': 'Aventador',
                    'LH': 'Huracán',
                    'LU': 'Urus'
                }
            },
            # Tesla (5YJ)
            '5YJ': {
                'model_codes': {
                    '3': 'Model 3',
                    'S': 'Model S',
                    'X': 'Model X',
                    'Y': 'Model Y'
                }
            },
            # Rivian (7FC)
            '7FC': {
                'model_codes': {
                    'R1': 'R1T',
                    'R2': 'R1S'
                }
            },
            # Lucid (7KR)
            '7KR': {
                'model_codes': {
                    'A1': 'Air'
                }
            },
            # Polestar (LPS)
            'LPS': {
                'model_codes': {
                    'CA': 'Polestar 2'
                }
            }
        }
# Year mapping for position 10
YEAR_MAP: Dict[str, int] = {
    'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984,
    'F': 1985, 'G': 1986, 'H': 1987, 'J': 1988, 'K': 1989,
    'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994,
    'S': 1995, 'T': 1996, 'U': 1997, 'V': 1998, 'W': 1999,
    'X': 2000, 'Y': 2001, '1': 2002, '2': 2003, '3': 2004,
    '4': 2005, '5': 2006, '6': 2007, '7': 2008, '8': 2009,
    '9': 2010, 'A': 2011, 'B': 2012, 'C': 2013, 'D': 2014,
    'E': 2015, 'F': 2016, 'G': 2017, 'H': 2018, 'J': 2019,
    'K': 2020, 'L': 2021, 'M': 2022, 'N': 2023, 'P': 2024,
    'R': 2025, 'S': 2026, 'T': 2027, 'U': 2028, 'V': 2029
}

# VIN weight factors for check digit calculation
WEIGHT_FACTORS: Dict[int, int] = {
    1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 10,
    9: 0, 10: 9, 11: 8, 12: 7, 13: 6, 14: 5, 15: 4,
    16: 3, 17: 2
}

# VIN character values for check digit calculation
TRANSLITERATION: Dict[str, int] = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '0': 0
}

# Valid VIN characters
VALID_CHARS = set('0123456789ABCDEFGHJKLMNPRSTUVWXYZ') 