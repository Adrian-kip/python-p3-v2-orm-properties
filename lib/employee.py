from __init__ import CURSOR, CONN
from department import Department


class Employee:
    """Represents an employee in the organization"""

    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        if len(name) == 0:
            raise ValueError("Name must not be empty")
        self._name = name

    @property
    def job_title(self):
        return self._job_title
    
    @job_title.setter
    def job_title(self, job_title):
        if not isinstance(job_title, str):
            raise ValueError("Job title must be a string")
        if len(job_title) == 0:
            raise ValueError("Job title must not be empty")
        self._job_title = job_title

    @property
    def department_id(self):
        return self._department_id
    
    @department_id.setter
    def department_id(self, department_id):
        if not isinstance(department_id, int):
            raise ValueError("Department ID must be an integer")
        if not Department.find_by_id(department_id):
            raise ValueError("Department ID must reference an existing department")
        self._department_id = department_id

    @classmethod
    def create_table(cls):
        """Create the employees table"""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the employees table"""
        sql = "DROP TABLE IF EXISTS employees;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Save employee to database"""
        sql = "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        """Create and save a new employee"""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        """Update employee in database"""
        sql = """
            UPDATE employees 
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete employee from database"""
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Create Employee instance from database row"""
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3])
            employee.id = row[0]
            cls.all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        """Get all employees"""
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Find employee by ID"""
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find employee by name"""
        sql = "SELECT * FROM employees WHERE name is ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @property
    def department(self):
        """Get the department this employee belongs to"""
        return Department.find_by_id(self.department_id)