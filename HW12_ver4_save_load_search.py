from datetime import datetime
from collections import UserDict
import re
import os
import pickle
import json

class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter # проверка формата номера телефона
    def value(self, value):
        if not re.match(r'^\+\d{2}-\d{3}-\d{3}-\d{2}-\d{2}$', value):
            raise ValueError("Phone number must be in the format of '+xx-xxx-xxx-xx-xx'")
        self.__value = value

class Mail(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, '%d-%m-%Y')
        except ValueError:
            raise ValueError("Birthdate must be in 'dd-mm-yyyy' format")

    def __str__(self):
        return self.__value.strftime('%d-%m-%Y')

class Record:
    def __init__(self, name, phone=None, mail=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self.mail = mail
        self.birthday = birthday
    
    def add_phone(self, phone):
        self.phones.append(phone)
    
    def edit_phone(self, index, phone):
        self.phones[index] = phone
    
    def delete_phone(self, index):
        del self.phones[index]
    
    def set_mail(self, mail):
        self.mail = mail
    
    def get_mail(self):
        return self.mail.value if self.mail else None
    
    def set_birthday(self, birthday):
        self.birthday = birthday
    
    def get_birthday(self):
        return self.birthday.value if self.birthday else None
    
    def days_to_birthday(self):

        if self.birthday:
            bd = self.birthday.value
            today = datetime.today().date()
            current_year_birthday = datetime(today.year, bd.month, bd.day).date()
            if current_year_birthday < today:
                current_year_birthday = datetime(today.year + 1, bd.month, bd.day).date()
            delta = current_year_birthday - today
            return delta.days
        return "The contact does not have a birthday"

class AddressBook(UserDict):


    def add_record(self, record):
        self.data[record.name.value] = record
        
    def edit_record(self, name, record):
        self.data[name.value] = record
        
    def delete_record(self, name):
        del self.data[name.value]
        
    def find_records(self, name):
        found_records = []
        for key in self.data:
            if name.lower() in key.lower():
                found_records.append(self.data[key])
        return found_records
    

####################################    
    def save_to_disk(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
        
        return('Address book saved successfully!')


    def load_from_disk(self, filename):
        
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
            return 'Address book loaded successfully!'
        return 'No file with contacts. Use empty.'
    

    def find_contact(self, search_str):
            found_records = []
            for key, value in self.data.items():
                if search_str in key or search_str in [phone.value for phone in value.phones]:
                    found_records.append(value)
            return found_records

##############################################
address_book = AddressBook()# create global variable

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Name not found in contacts"
    return inner

def hello():
    print("""Hello, I'm a bot. I will help you use the program.
        - For add contact to directory input <<< add 'name' 'phone number in format '+xx-xxx-xxx-xx-xx', 'email', 'Birthdate' in format dd-mm-yyyy'  >>> use a space without a comma
        - For find contact in directory input <<< find 'name'  >>> use a space without a comma
        - For search contact by name letters, input <<< search name letters
        - For show all contacts in directory input <<< show >>> 
        - For update contact in directory input <<< update 'name' 'new number'  >>> use a space without a comma
        - For return the number of days until the next birthday, enter <<<dtb "name">>>.
        - To exit the program input <<<exit>>> or <<<bye>>>""")

@input_error

def add_contact(*args):
    name_field = Name(args[0])
    phone_field = Phone(args[1])
    mail_field = Mail(args[2]) if len(args) > 2 else None
    birthday_field = Birthday(args[3]) if len(args) > 3 else None
    rec:Record = address_book.get(name_field.value)


    if rec:
        
        rec.add_phone(phone_field)
        if mail_field:
            rec.set_mail(mail_field)
        if birthday_field:
            rec.birthday = birthday_field
    
    else:
        rec = Record(name_field, phone_field, mail_field, birthday_field)
        address_book.add_record(rec)
        return f"Contact {name_field} with phone number {phone_field} added successfully"


    return address_book

@input_error
def days_to_birthday(name):
    name_field = Name(name)
    rec:Record = address_book.get(name_field.value)
    if rec:
        return rec.days_to_birthday()
    
    else:
        return f"No record found with name1 {name}"

@input_error
def find_contact(name):
    name_field = Name(name)
    found_records = address_book.find_records(name_field.value)
    if found_records:
        for record in found_records:
            email = record.get_mail()
            if not email:
                email_str = f", {email}"
            else:
                email_str = email
        for record in found_records:
            birthday = record.get_birthday()
            if not birthday:
                birthday_str = f", {birthday}"
            else:
                birthday_str = birthday    
        return f"{record.name.value}: {', '.join(str(phone) for phone in record.phones)} | {email_str} | {birthday_str}"
    else:
        return f"No records found for {name}"

@input_error
def update_contact(name, phone, mail=None):
    name_field = Name(name)
    if name_field.value in address_book:
        record = address_book[name_field.value]
        record.edit_phone(0, phone)
        if mail:
            mail_field = Mail(mail)
            record.set_mail(mail_field)
        return f"Updated phone number and email for {name} to {phone} and {mail}"
    else:
        phone_field = Phone(phone)
        mail_field = Mail(mail) if mail else None
        record = Record(name_field, phone_field, mail_field)
        address_book.add_record(record)
        return f"Added {name} with phone number {phone} and email {mail}"
    return address_book

@input_error
def show_all_contacts():
    
    if len(address_book.data) == 0:
        print("No contacts found")
    else:
        print("All contacts:")
        for name in address_book.data:
            record = address_book.data[name]
            email = record.get_mail()
            if not email:
                email_str = f", {email}"
            else:
                email_str = email
        for name in address_book.data:
            record = address_book.data[name]
            birthday = record.get_birthday()
            if not birthday:
                birthday_str = f", {birthday}"
            else:
                birthday_str = birthday
            print(f"{record.name.value}: {', '.join(str(phone) for phone in record.phones)} | {email_str}  |  {birthday_str}")

###############################
@input_error
def save(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f)

@input_error
def load(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)
#############################

def parse_command(command, filename = None):
    parts = command.split()
    command_list = command.split()
    operation = command_list[0]

    if parts[0] == "hello":
        hello()
    
    elif parts[0] == "add":
        if len(parts) <= 1:
            try:
                raise IndexError
            except IndexError:
                return "Command to add contact is empty, please repeat with name and number"
        else:
            
            return add_contact(*parts[1:])
    
    elif parts[0] == "find":
        if len(parts) < 1:
            raise IndexError
        return find_contact(parts[1])

    elif parts[0] == "update":
        if len(parts) < 4:
            raise IndexError
        return update_contact(parts[1], parts[2])

    elif parts[0] == "show":
        if len(parts)<1:
            raise IndexError
        return show_all_contacts()

    elif parts[0] == "dtb":

        if len(parts)<1:
            raise IndexError
        return days_to_birthday(parts[1])
    

    elif operation == "search":
        # code for finding a contact by name or phone number
        search_str = command_list[1]
        found_contacts = address_book.find_contact(search_str)
        if found_contacts:
            for contact in found_contacts:
                print(f"{contact.name}: {contact.phones} | {contact.mail} | {contact.birthday}")
        else:
            print("No contacts found.")
    
    #############################
    
    elif parts[0] == "save":
        if filename is None: # имя по умолчанию
        
            filename = "data.bin"
        address_book.save_to_disk(filename)
        print("Data saved successfully to", filename)     
    
    elif parts[0] == "load":
        if filename is None:
            filename = "data.bin"
        address_book.load_from_disk(filename)
        print("Data loaded successfully from", filename)
        
    else:
        return "Invalid command"
############################

def main():
    while True:
        command = input("Enter command: ")
        if command == "exit" or command == "bye":
            print("The program is finished")
            break
        else:
            print(parse_command(command))

if __name__ == '__main__':
    main()



