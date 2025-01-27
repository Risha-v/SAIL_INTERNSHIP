from typing import Tuple, List, Dict, Any, Set
import random
from datetime import datetime, timedelta
import csv


class DataConstants:
    FIRST_NAMES = [
        'Aarav', 'Advait', 'Agastya', 'Akshay', 'Anant', 'Arnav', 'Arjun', 'Atharv',
        'Ayush', 'Bharat', 'Chakresh', 'Daksh', 'Darsh', 'Dev', 'Dhruv', 'Eshan',
        'Gaurav', 'Harsh', 'Hemant', 'Ishaan', 'Kabir', 'Kartik', 'Keshav', 'Krishna',
        'Lakshay', 'Manan', 'Neel', 'Nirvaan', 'Om', 'Pranav', 'Reyansh', 'Riddhi',
        'Rishabh', 'Rohan', 'Rudra', 'Samar', 'Shaurya', 'Shivansh', 'Siddharth', 'Tanay',
        'Tejas', 'Udayan', 'Veer', 'Vihaan', 'Virat', 'Vivaan', 'Yash', 'Yuvan',
        'Madhav', 'Parth', 'Aadya', 'Aanvi', 'Aditi', 'Ahana', 'Amara', 'Ananya', 'Anika', 'Anvi',
        'Aparajita', 'Avani', 'Chahana', 'Diya', 'Divya', 'Gauri', 'Geetika', 'Hansika',
        'Ira', 'Ishika', 'Jwala', 'Kaavya', 'Kashvi', 'Keya', 'Kiara', 'Lasya',
        'Lavanya', 'Mahika', 'Mira', 'Naira', 'Navya', 'Nisha', 'Ojaswini', 'Palak',
        'Pihu', 'Rashi', 'Ridhi', 'Saanvi', 'Sahana', 'Samaira', 'Shanaya', 'Tara',
        'Trisha', 'Uma', 'Vanya', 'Vedika', 'Veda', 'Vidhi', 'Yashi', 'Zara',
        'Nitya', 'Ishani'
    ]

    LAST_NAMES = [
        'Acharya', 'Adhikari', 'Ahuja', 'Apte', 'Arora', 'Athreya', 'Bajaj', 'Bakshi',
        'Balakrishnan', 'Basu', 'Bhagat', 'Bhandari', 'Bhardwaj', 'Bhat', 'Bhatnagar',
        'Bhowmik', 'Birla', 'Biswas', 'Bose', 'Chakraborty', 'Chand', 'Chandran',
        'Chaturvedi', 'Chawla', 'Dasgupta', 'Deshpande', 'Devan', 'Dewan', 'Dharma',
        'Dhillon', 'Dwivedi', 'Ganesan', 'Ghosh', 'Gokhale', 'Gowda', 'Gulati',
        'Hegde', 'Hora', 'Iyengar', 'Iyer', 'Jadhav', 'Jaggi', 'Jaiswal',
        'Jindal', 'Johar', 'Juneja', 'Kadak', 'Kale', 'Kalra', 'Kanda', 'Kannan',
        'Kar', 'Kashyap', 'Kaur', 'Khanna', 'Khatri', 'Krishna', 'Kulkarni', 'Kumar',
        'Kurup', 'Lamba', 'Mahajan', 'Maitra', 'Mane', 'Mangal', 'Mehra', 'Mhatre',
        'Mitra', 'Murthy', 'Nag', 'Nanda', 'Narang', 'Nehru', 'Oak', 'Pai',
        'Parikh', 'Prabhu', 'Pradhan', 'Prakash', 'Rajan', 'Rajput', 'Raman',
        'Ramanathan', 'Rathi', 'Roshan', 'Sabharwal', 'Sachdeva', 'Sami', 'Sankaran',
        'Saxena', 'Sen', 'Seshadri', 'Sethi', 'Shankar', 'Shastri', 'Shinde',
        'Shukla', 'Suri', 'Swamy', 'Tagore', 'Tandon', 'Tyagi', 'Varma'
    ]

    DEPARTMENTS = [
        'Finance', 'HR', 'Operations', 'IT', 'Production', 'Quality Control', 
        'Maintenance', 'Safety', 'Supply Chain', 'R&D'
    ]

    SHOPS = [
        'Mining', 'Blast Furnace 1', 'Blast Furnace 2', 'Blast Furnace 3', 
        'Blast Furnace 4', 'Blast Furnace 5', 'SMS', 'HSM', 'CRM', 'Sinter Plant', 
        'Machine Shop', 'Structural Shop', 'Coke Oven'
    ]

    MANAGER_DESIGNATIONS = [
        'Junior Manager', 'Assistant Manager', 'Deputy Manager', 'Manager', 'Senior Manager'
    ]

    EXECUTIVE_DESIGNATIONS = [
        'AGM', 'DGM', 'GM', 'CGM', 'ED', 'Director', 'Chairman'
    ]

    BANKS = [
        ('State Bank of India', 'SBIN'),
        ('Punjab National Bank', 'PUNB'),
        ('Bank of Baroda', 'BARB'),
        ('HDFC Bank', 'HDFC'),
        ('ICICI Bank', 'ICIC'),
        ('Union Bank of India', 'UBIN')
    ]

    BRANCHES = [
        'Main Branch', 'Civil Lines', 'Sector 4', 'Industrial Area', 'City Center',
        'Station Road', 'Steel Plant Branch', 'Township Branch'
    ]


class EmployeeGenerator:
    def __init__(self):
        self.constants = DataConstants()
        self.name_mapping = self.create_name_mapping()

    def create_name_mapping(self) -> Dict[str, List[str]]:
        """Create a mapping of each first name to a unique set of last names."""
        first_names = self.constants.FIRST_NAMES
        last_names = self.constants.LAST_NAMES
        mapping = {}
        for i, first_name in enumerate(first_names):
            mapping[first_name] = [
                last_names[(i * 100 + j) % len(last_names)] for j in range(100)
            ]
        return mapping

    def generate_employee_ids(self, count: int) -> List[int]:
        """Generate a set of unique 7-digit employee IDs."""
        employee_ids: Set[int] = set()
        while len(employee_ids) < count:
            emp_id = random.randint(1000000, 9999999)
            employee_ids.add(emp_id)
        return sorted(list(employee_ids))

    def generate_unique_full_name(self, existing_names: Set[str]) -> Tuple[str, str]:
        """Generate a unique full name that doesn't already exist."""
        while True:
            first_name = random.choice(list(self.name_mapping.keys()))
            last_name = random.choice(self.name_mapping[first_name])
            full_name = f"{first_name} {last_name}"
            if full_name not in existing_names:
                existing_names.add(full_name)
                return first_name, last_name

    def generate_phone_number(self) -> str:
        return f"9{random.randint(100000000, 999999999)}"

    def generate_account_number(self) -> str:
        return str(random.randint(10000000000, 99999999999999999))

    def generate_ifsc_code(self, bank_code: str) -> str:
        return f"{bank_code}{random.randint(10000, 99999)}"

    def generate_date_of_joining(self) -> str:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2023, 12, 31)
        days_between = (end_date - start_date).days
        random_days = random.randrange(days_between)
        return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

    def generate_quarter_no(self) -> str:
        if random.random() < 0.6:  # 60% chance of having a quarter
            second_digit = random.randint(1, 9)
            third_digit = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            quarter_type = random.choice(['A', 'B', 'C', 'D'])
            quarter_no = random.randint(1799, 2099)
            return f"0{second_digit}{third_digit}{quarter_type}{quarter_no}"
        return ""

    def generate_employee_data(self, emp_id: int, existing_names: Set[str]) -> Dict[str, Any]:
        first_name, last_name = self.generate_unique_full_name(existing_names)

        role_type = random.choices(
            ['Worker', 'Officer', 'Manager', 'Executive'],
            weights=[40, 30, 20, 10]
        )[0]

        if role_type == 'Worker':
            grade = f"S{random.randint(1, 5)}"
            designation = f"Worker "
        elif role_type == 'Officer':
            grade = f"S{random.randint(6, 11)}"
            designation = f"Supervisor "
        elif role_type == 'Manager':
            grade = ''
            designation = random.choice(self.constants.MANAGER_DESIGNATIONS)
        else:
            grade = ''
            designation = random.choice(self.constants.EXECUTIVE_DESIGNATIONS)

        bank_name, bank_code = random.choice(self.constants.BANKS)
        branch_name = random.choice(self.constants.BRANCHES)
        quarter_no = self.generate_quarter_no()

        return {
            'employee_id': str(emp_id),
            'first_name': first_name,
            'last_name': last_name,
            'designation': designation,
            'department': random.choice(self.constants.DEPARTMENTS),
            'grade': grade,
            'date_of_joining': self.generate_date_of_joining(),
            'quarter_no': quarter_no,
            'has_quarter': 'Yes' if quarter_no else 'No',
            'email_id': f"{first_name.lower()}.{last_name.lower()}@sail.bokaro.com",
            'phone_number': self.generate_phone_number(),
            'account_number': self.generate_account_number(),
            'ifsc_code': self.generate_ifsc_code(bank_code),
            'branch_name': branch_name,
            'bank_name': bank_name,
            'shop': random.choice(self.constants.SHOPS)
        }

    def generate_employees(self, num_employees: int) -> List[Dict[str, Any]]:
        employee_ids = self.generate_employee_ids(num_employees)
        existing_names = set()
        return [self.generate_employee_data(emp_id, existing_names) for emp_id in employee_ids]


class PayStructureGenerator:
    def __init__(self):
        self.salary_ranges = {
            'Worker': (20000, 28000),
            'Supervisor': (44000, 57000),
            'Manager': (73000, 92000),
            'Executive': (145000, 205000)
        }
        
        self.da_percent = 0.20
        self.hra_percent = 0.30
        
        self.medical_benefits = {
            'Worker': 5000,
            'Supervisor': 8000,
            'Manager': 12000,
            'Executive': (20000, 25000)
        }
        
        self.bonus_ranges = {
            'Worker': (7500, 10000),
            'Supervisor': (14500, 19000),
            'Manager': (21500, 24250),
            'Executive': (25000, 25000)
        }

    def generate_base_salary(self, role: str) -> float:
        min_salary, max_salary = self.salary_ranges[role]
        return round(random.uniform(min_salary, max_salary), -3)

    def calculate_allowances(self, base_salary: float, role: str, has_quarter: bool) -> Dict[str, Any]:
        allowances = {
            'da': round(base_salary * self.da_percent),
            'hra': 0 if has_quarter else round(base_salary * self.hra_percent),
            'medical_benefits': (
                random.randint(*self.medical_benefits[role]) 
                if isinstance(self.medical_benefits[role], tuple) 
                else self.medical_benefits[role]
            ),
            'bonus_amount': random.randint(*self.bonus_ranges[role]),
            'other_allowances': round(base_salary * random.uniform(0.05, 0.08))
        }

        allowances['ta'] = (
            None if role == 'Worker'
            else round(base_salary * random.uniform(0.08, 0.12))
        )
        
        allowances['stocks'] = (
            round(base_salary * random.uniform(0.3, 0.35))
            if role == 'Executive'
            else None
        )
        
        allowances['vacation_tour'] = (
            round(base_salary * random.uniform(0.15, 0.20))
            if role in ['Manager', 'Executive']
            else None
        )
        
        allowances['uniform_allowance'] = (
            2000 if role in ['Worker', 'Supervisor']
            else None
        )

        return allowances

    def get_role_from_designation(self, designation: str) -> str:
        if 'Worker' in designation:
            return 'Worker'
        elif 'Supervisor' in designation:
            return 'Supervisor'
        elif 'Manager' in designation:
            return 'Manager'
        else:
            return 'Executive'

    def generate_pay_structure(self, employee: Dict[str, Any]) -> Dict[str, Any]:
        role = self.get_role_from_designation(employee['designation'])
        has_quarter = employee['has_quarter'] == 'Yes'
        
        base_salary = self.generate_base_salary(role)
        allowances = self.calculate_allowances(base_salary, role, has_quarter)
        
        return {
            'pay_id': int(employee['employee_id']),
            'employee_id': employee['employee_id'],
            'base_salary': base_salary,
            **allowances
        }

def save_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully generated {filename} with {len(data)} records!")
    except Exception as e:
        print(f"An error occurred while saving {filename}: {str(e)}")

def main():
    # Generate employee data
    num_employees = 10000
    employee_generator = EmployeeGenerator()
    employees = employee_generator.generate_employees(num_employees)

    # Remove duplicate employee IDs if any
    unique_employees = {emp['employee_id']: emp for emp in employees}.values()
    employees = list(unique_employees)

    # Save employee data
    employee_headers = [
        'employee_id', 'first_name', 'last_name', 'designation', 'department',
        'grade', 'date_of_joining', 'quarter_no', 'has_quarter', 'email_id',
        'phone_number', 'account_number', 'ifsc_code', 'branch_name',
        'bank_name', 'shop'
    ]
    save_to_csv(employees, 'psu_employees.csv', employee_headers)

    # Generate and save pay structure data
    pay_generator = PayStructureGenerator()
    pay_structures = [pay_generator.generate_pay_structure(emp) for emp in employees]

    # Remove duplicates from pay structure data
    unique_pay_structures = {ps['employee_id']: ps for ps in pay_structures}.values()
    pay_structures = list(unique_pay_structures)

    pay_headers = [
        'pay_id', 'employee_id', 'base_salary', 'ta', 'da', 'hra',
        'stocks', 'vacation_tour', 'uniform_allowance',
        'medical_benefits', 'bonus_amount', 'other_allowances'
    ]
    save_to_csv(pay_structures, 'pay_structure.csv', pay_headers)

    print("Data generation and saving completed successfully!")

if __name__ == "__main__":
    main()
