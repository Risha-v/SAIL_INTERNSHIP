import pandas as pd
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from datetime import datetime
import re
import os
from typing import Optional, Tuple, Any, Set
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class DatabaseManager:
    def __init__(self, host: str, user: str, password: str, port: str = "5432"):
        """Initialize DatabaseManager with connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.db_name = "employeedb"
        self.conn = None
        self.cur = None
        self.max_retries = 5
        self.retry_delay = 3
        self.successful_employee_ids = set()

    def connect_to_default_db(self) -> None:
        """Connect to default postgres database to create our new database"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database="postgres"
            )
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.conn.cursor()
            logging.info("Successfully connected to default database")
        except Error as e:
            logging.error(f"Error connecting to default database: {e}")
            raise

    def create_database(self) -> None:
        """Create the database with proper case handling"""
        try:
            # Check if database exists before attempting to terminate connections
            self.cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            if self.cur.fetchone():
                # Terminate existing connections
                self.cur.execute("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s
                    AND pid <> pg_backend_pid();
                """, (self.db_name,))
            
            # Drop and create database
            self.cur.execute(f'DROP DATABASE IF EXISTS "{self.db_name}"')
            self.cur.execute(f'CREATE DATABASE "{self.db_name}"')
            logging.info(f"Database {self.db_name} created successfully")
            
            # Close current connection
            self.cleanup()
            
            # Wait for database to be ready
            time.sleep(5)
            
        except Error as e:
            logging.error(f"Error creating database: {e}")
            raise

    def verify_database_exists(self) -> bool:
        """Verify that the database exists"""
        try:
            with psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database="postgres"
            ) as temp_conn:
                temp_conn.autocommit = True
                with temp_conn.cursor() as temp_cur:
                    temp_cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
                    exists = temp_cur.fetchone() is not None
                    
                    if exists:
                        logging.info(f"Verified database {self.db_name} exists")
                    else:
                        logging.error(f"Database {self.db_name} does not exist")
                    
                    return exists
                    
        except Error as e:
            logging.error(f"Error verifying database: {e}")
            return False

    def connect_to_psu_db(self) -> None:
        """Connect to the employeedb database with retry logic"""
        if not self.verify_database_exists():
            raise Exception(f"Database {self.db_name} does not exist")
            
        for attempt in range(self.max_retries):
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    database=self.db_name
                )
                self.conn.autocommit = True
                self.cur = self.conn.cursor()
                logging.info(f"Successfully connected to {self.db_name}")
                return
            except Error as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logging.warning(f"Connection attempt {attempt + 1} failed, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Error connecting to {self.db_name} after {self.max_retries} attempts: {e}")
                    raise

    def create_tables(self) -> None:
        """Create the necessary tables with constraints"""
        try:
            # Create Employees table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INTEGER PRIMARY KEY CHECK (employee_id BETWEEN 1000000 AND 9999999),
                    first_name VARCHAR(50) NOT NULL CHECK (first_name ~ '^[A-Za-z]+$'),
                    last_name VARCHAR(50) NOT NULL CHECK (last_name ~ '^[A-Za-z]+$'),
                    designation VARCHAR(50) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    grade VARCHAR(10) DEFAULT 'NA',
                    date_of_joining DATE NOT NULL,
                    quarter_no VARCHAR(10) DEFAULT 'NA' CHECK (quarter_no ~ '^[0-9]{2}[A-Z]{2}[0-9]{4}$' OR quarter_no = 'NA'),
                    email_id VARCHAR(100) NOT NULL UNIQUE 
                        CHECK (email_id ~ '^[a-zA-Z]+[.][a-zA-Z]+@sail[.]bokaro[.]com$'),
                    phone_number VARCHAR(10) NOT NULL CHECK (phone_number ~ '^[0-9]{10}$'),
                    account_number VARCHAR(20) NOT NULL CHECK (account_number ~ '^[0-9]{1,20}$'),
                    ifsc_code VARCHAR(20) NOT NULL CHECK (ifsc_code ~ '^[A-Z]{4}[0-9]{5,}$'),
                    branch_name VARCHAR(50) NOT NULL,
                    bank_name VARCHAR(50) NOT NULL,
                    shop VARCHAR(50) NOT NULL
                )
            """)

            # Create PayStructure table with new columns
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS pay_structure (
                    pay_id INTEGER PRIMARY KEY,
                    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    base_salary NUMERIC(10,2) NOT NULL CHECK (base_salary > 20000),
                    ta NUMERIC(10,2) DEFAULT 0,
                    da NUMERIC(10,2) NOT NULL CHECK (da >= 0),
                    hra NUMERIC(10,2) NOT NULL CHECK (hra >= 0),
                    stocks NUMERIC(10,2) DEFAULT 0 CHECK (stocks >= 0),
                    vacation_tour NUMERIC(10,2) DEFAULT 0 CHECK (vacation_tour >= 0),
                    uniform_allowance NUMERIC(10,2) DEFAULT 0,
                    medical_benefits NUMERIC(10,2) NOT NULL CHECK (medical_benefits >= 0),
                    bonus_amount NUMERIC(10,2) NOT NULL CHECK (bonus_amount <= 25000),
                    other_allowances NUMERIC(10,2) DEFAULT 0,
                    employee_pf NUMERIC(10,2) GENERATED ALWAYS AS (base_salary * 0.125) STORED,
                    employer_pf NUMERIC(10,2) GENERATED ALWAYS AS (base_salary * 0.125) STORED,
                    total_pf NUMERIC(10,2) GENERATED ALWAYS AS (base_salary * 0.25) STORED,
                    income_tax NUMERIC(10,2),
                    monthly_salary NUMERIC(10,2) GENERATED ALWAYS AS (
                        base_salary + 
                        COALESCE(ta, 0) + 
                        COALESCE(da, 0) + 
                        COALESCE(hra, 0) + 
                        COALESCE(uniform_allowance, 0) - 
                        (base_salary * 0.125) -  -- Subtract employee PF
                        COALESCE(income_tax, 0)  -- Subtract income tax
                    ) STORED
                )
            """)

            # Create indexes for frequent queries
            self.cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_employee_email ON employees(email_id);
                CREATE INDEX IF NOT EXISTS idx_employee_department ON employees(department);
                CREATE INDEX IF NOT EXISTS idx_pay_employee_id ON pay_structure(employee_id);
            """)

            # Create function to calculate income tax
            self.cur.execute("""
                CREATE OR REPLACE FUNCTION calculate_income_tax(annual_income NUMERIC)
                RETURNS NUMERIC AS $$
                DECLARE
                    tax NUMERIC := 0;
                BEGIN
                    -- New tax regime 2023-24
                    IF annual_income <= 300000 THEN
                        tax := 0;
                    ELSIF annual_income <= 600000 THEN
                        tax := (annual_income - 300000) * 0.05;
                    ELSIF annual_income <= 900000 THEN
                        tax := 15000 + (annual_income - 600000) * 0.10;
                    ELSIF annual_income <= 1200000 THEN
                        tax := 45000 + (annual_income - 900000) * 0.15;
                    ELSIF annual_income <= 1500000 THEN
                        tax := 90000 + (annual_income - 1200000) * 0.20;
                    ELSE
                        tax := 150000 + (annual_income - 1500000) * 0.30;
                    END IF;
                    
                    -- Return monthly tax
                    RETURN ROUND(tax / 12, 2);
                END;
                $$ LANGUAGE plpgsql;
            """)

            logging.info("Tables, indexes, and functions created successfully")
        except Error as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def validate_ifsc_code(self, ifsc_code: str) -> bool:
        """Validate IFSC code format"""
        if pd.isna(ifsc_code):
            return False
        ifsc_code = str(ifsc_code).strip()
        return bool(re.match(r'^[A-Z]{4}[0-9]{5,}$', ifsc_code))

    def validate_employee_data(self, row: pd.Series) -> Tuple[bool, Optional[str]]:
        """Validate employee data before insertion"""
        try:
            # Validate employee_id
            if not (1000000 <= int(row['employee_id']) <= 9999999):
                return False, f"Invalid employee_id: {row['employee_id']}"

            # Validate names
            if not re.match(r'^[A-Za-z]+$', str(row['first_name'])):
                return False, f"Invalid first_name: {row['first_name']}"
            if not re.match(r'^[A-Za-z]+$', str(row['last_name'])):
                return False, f"Invalid last_name: {row['last_name']}"

            # Validate date
            try:
                datetime.strptime(str(row['date_of_joining']), '%Y-%m-%d')
            except ValueError:
                return False, f"Invalid date_of_joining: {row['date_of_joining']}"

            # Validate quarter_no if not 'NA'
            if str(row['quarter_no']) != 'NA':
                if not re.match(r'^[0-9]{2}[A-Z]{2}[0-9]{4}$', str(row['quarter_no'])):
                    return False, f"Invalid quarter_no: {row['quarter_no']}"

            # Validate email
            if not re.match(r'^[a-zA-Z]+[.][a-zA-Z]+@sail[.]bokaro[.]com$', str(row['email_id'])):
                return False, f"Invalid email_id: {row['email_id']}"

            # Validate phone number
            if not re.match(r'^[0-9]{10}$', str(row['phone_number'])):
                return False, f"Invalid phone_number: {row['phone_number']}"

            # Validate IFSC code
            if not self.validate_ifsc_code(row['ifsc_code']):
                return False, f"Invalid ifsc_code: {row['ifsc_code']}"

            # Validate account number
            if not re.match(r'^[0-9]{1,20}$', str(row['account_number'])):
                return False, f"Invalid account_number: {row['account_number']}"

            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def validate_pay_data(self, row: pd.Series) -> Tuple[bool, Optional[str]]:
        """Validate pay structure data before insertion"""
        try:
            # Validate numeric fields
            if float(row['base_salary']) <= 20000:
                return False, f"Invalid base_salary: {row['base_salary']}"

            # Validate non-negative values
            for field in ['da', 'hra', 'stocks', 'vacation_tour', 'medical_benefits']:
                if float(row[field]) < 0:
                    return False, f"Invalid {field}: {row[field]}"

            # Validate bonus amount
            if float(row['bonus_amount']) > 25000:
                return False, f"Invalid bonus_amount: {row['bonus_amount']}"

            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def import_data(self, employee_file: str, pay_file: str) -> None:
        """Import data from CSV files with improved error handling"""
        try:
            # Import employee data first
            employees_df = pd.read_csv(employee_file)
            # Replace NaN with 'NA' for employee table
            employees_df = employees_df.fillna('NA')
            
            successful_inserts = 0
            failed_inserts = 0

            for _, row in employees_df.iterrows():
                if 'ifsc_code' in row:
                    row['ifsc_code'] = str(row['ifsc_code']).strip()
                
                is_valid, error_msg = self.validate_employee_data(row)
                if is_valid:
                    try:
                        values = [
                            int(row['employee_id']), str(row['first_name']), str(row['last_name']),
                            str(row['designation']), str(row['department']), str(row['grade']),
                            str(row['date_of_joining']), str(row['quarter_no']), str(row['email_id']),
                            str(row['phone_number']), str(row['account_number']), str(row['ifsc_code']),
                            str(row['branch_name']), str(row['bank_name']), str(row['shop'])
                        ]
                        
                        self.cur.execute("""
                            INSERT INTO employees (
                                employee_id, first_name, last_name, designation,
                                department, grade, date_of_joining, quarter_no,
                                email_id, phone_number, account_number, ifsc_code,
                                branch_name, bank_name, shop
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, values)
                        
                        self.successful_employee_ids.add(int(row['employee_id']))
                        successful_inserts += 1
                    except Error as e:
                        logging.warning(f"Error inserting employee record: {e}")
                        failed_inserts += 1
                else:
                    logging.warning(f"Skipping invalid employee record: {error_msg}")
                    failed_inserts += 1

            logging.info(f"Employees import completed - Successful: {successful_inserts}, Failed: {failed_inserts}")

            # Import pay structure data
            pay_df = pd.read_csv(pay_file)
            
            # Replace NaN with 0 for nullable columns
            nullable_columns = ['ta', 'stocks', 'vacation_tour', 'uniform_allowance', 'other_allowances']
            pay_df[nullable_columns] = pay_df[nullable_columns].fillna(0)
            
            # Calculate annual income for tax purposes
            pay_df['annual_income'] = (
                pay_df['base_salary'] * 12 +
                pay_df['ta'] * 12 +
                pay_df['da'] * 12 +
                pay_df['hra'] * 12 +
                pay_df['uniform_allowance'] * 12 +
                pay_df['stocks'] +  # 
                pay_df['vacation_tour'] +  # 
                pay_df['medical_benefits'] +  # 
                pay_df['bonus_amount']  # 
            )
            
            pay_successful = 0
            pay_failed = 0

            for _, row in pay_df.iterrows():
                if int(row['employee_id']) in self.successful_employee_ids:
                    is_valid, error_msg = self.validate_pay_data(row)
                    if is_valid:
                        try:
                            # Calculate monthly income tax
                            self.cur.execute(
                                "SELECT calculate_income_tax(%s)",
                                (float(row['annual_income']),)
                            )
                            monthly_tax = self.cur.fetchone()[0]
                            
                            values = (
                                int(row['pay_id']), 
                                int(row['employee_id']), 
                                float(row['base_salary']),
                                float(row['ta']), 
                                float(row['da']), 
                                float(row['hra']), 
                                float(row['stocks']),
                                float(row['vacation_tour']), 
                                float(row['uniform_allowance']),
                                float(row['medical_benefits']), 
                                float(row['bonus_amount']),
                                float(row['other_allowances']), 
                                float(monthly_tax)
                            )
                            
                            self.cur.execute("""
                                INSERT INTO pay_structure (
                                    pay_id, employee_id, base_salary, ta, da, hra,
                                    stocks, vacation_tour, uniform_allowance,
                                    medical_benefits, bonus_amount, other_allowances,
                                    income_tax
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, values)
                            
                            pay_successful += 1
                        except Error as e:
                            logging.warning(f"Error inserting pay record: {e}")
                            pay_failed += 1
                    else:
                        logging.warning(f"Skipping invalid pay record: {error_msg}")
                        pay_failed += 1
                else:
                    logging.warning(f"Skipping pay record for non-existent employee_id: {row['employee_id']}")
                    pay_failed += 1

            logging.info(f"Pay structure import completed - Successful: {pay_successful}, Failed: {pay_failed}")

        except Exception as e:
            logging.error(f"Error importing data: {e}")
            raise

    def create_total_compensation_function(self) -> None:
        """Create a function to calculate total compensation (including annual benefits)"""
        try:
            self.cur.execute("""
                CREATE OR REPLACE FUNCTION calculate_total_compensation(p_employee_id INTEGER)
                RETURNS TABLE(
                    monthly_compensation NUMERIC,
                    annual_compensation NUMERIC,
                    total_benefits NUMERIC
                ) AS $$
                DECLARE
                    monthly_comp NUMERIC;
                    annual_comp NUMERIC;
                    annual_benefits NUMERIC;
                BEGIN
                    -- Calculate monthly compensation
                    SELECT monthly_salary INTO monthly_comp
                    FROM pay_structure
                    WHERE employee_id = p_employee_id;
                    
                    -- Calculate annual benefits
                    SELECT 
                        COALESCE(stocks, 0) + 
                        COALESCE(vacation_tour, 0) + 
                        medical_benefits +
                        bonus_amount INTO annual_benefits
                    FROM pay_structure
                    WHERE employee_id = p_employee_id;
                    
                    -- Calculate annual compensation
                    annual_comp := (COALESCE(monthly_comp, 0) * 12) + COALESCE(annual_benefits, 0);
                    
                    RETURN QUERY SELECT 
                        COALESCE(monthly_comp, 0),
                        COALESCE(annual_comp, 0),
                        COALESCE(annual_benefits, 0);
                END;
                $$ LANGUAGE plpgsql;
            """)
            logging.info("Total compensation function created successfully")
        except Error as e:
            logging.error(f"Error creating total compensation function: {e}")
            raise

    def create_employee_summary_view(self) -> None:
        """Create a comprehensive view for employee summary information"""
        try:
            self.cur.execute("""
                CREATE OR REPLACE VIEW employee_summary AS
                SELECT 
                    e.employee_id,
                    e.first_name || ' ' || e.last_name as full_name,
                    e.department,
                    e.designation,
                    e.grade,
                    p.base_salary,
                    p.monthly_salary as net_monthly_salary,
                    p.employee_pf as monthly_pf_deduction,
                    p.employer_pf as monthly_company_pf,
                    p.income_tax as monthly_tax,
                    comp.monthly_compensation,
                    comp.annual_compensation,
                    comp.total_benefits as annual_benefits,
                    e.date_of_joining,
                    e.email_id,
                    e.phone_number
                FROM employees e
                LEFT JOIN pay_structure p ON e.employee_id = p.employee_id
                CROSS JOIN LATERAL calculate_total_compensation(e.employee_id) comp;
            """)
            logging.info("Employee summary view created successfully")
        except Error as e:
            logging.error(f"Error creating employee summary view: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up database connections"""
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
            logging.info("Database connections cleaned up")
        except Error as e:
            logging.error(f"Error during cleanup: {e}")

def main():
    """Main function to set up the database and import data"""
    # Database connection parameters
    DB_PARAMS = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 'password',  #Replace with the correct password
        'port': '5432'
    }

    # Initialize database manager
    db_manager = DatabaseManager(**DB_PARAMS)

    try:
        # Setup database and tables
        db_manager.connect_to_default_db()
        db_manager.create_database()
        
        # Additional delay after database creation
        time.sleep(3)
        
        db_manager.connect_to_psu_db()
        db_manager.create_tables()

        # Import data if CSV files exist
        if os.path.exists('psu_employees.csv') and os.path.exists('pay_structure.csv'):
            db_manager.import_data('psu_employees.csv', 'pay_structure.csv')
            db_manager.create_total_compensation_function()
            db_manager.create_employee_summary_view()
            logging.info("Data import and function creation completed successfully")
        else:
            logging.warning("CSV files not found, skipping data import")

        logging.info("Database setup completed successfully")

    except Exception as e:
        logging.error(f"Database setup failed: {e}")
        raise
    finally:
        db_manager.cleanup()

if __name__ == "__main__":
    main()