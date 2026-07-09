import pandas as pd

# Load CSV files
customers = pd.read_csv("../data/customers.csv")
products = pd.read_csv("../data/products.csv")
sales = pd.read_csv("../data/sales.csv")

# Display first 5 rows
print("Customers")
print(customers.head())

print("\nProducts")
print(products.head())

print("\nSales")
print(sales.head())

# -------------------------------
# Explore the customers dataset
# -------------------------------

print("\nLast 5 Customers")
print(customers.tail())

print("\nShape of Customers Dataset")
print(customers.shape)

print("\nCustomer Columns")
print(customers.columns)

print("\nCustomer Dataset Information")
customers.info()

print("\nCustomer Statistics")
print(customers.describe())



print("\n---------------------------")
print("Missing Values")
print("---------------------------")
print(customers.isnull().sum())

print("\n---------------------------")
print("Duplicate Rows")
print("---------------------------")
print(customers.duplicated().sum())