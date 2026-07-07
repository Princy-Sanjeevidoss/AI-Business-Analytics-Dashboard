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