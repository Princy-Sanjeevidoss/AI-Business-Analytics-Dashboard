import pandas as pd
import matplotlib.pyplot as plt

# Load sales data
sales = pd.read_csv("../data/sales.csv")

# Total sales by product
sales_by_product = sales.groupby("product_id")["total_amount"].sum()

# Create bar chart
plt.figure(figsize=(8, 5))
plt.bar(sales_by_product.index.astype(str), sales_by_product.values)

plt.title("Sales by Product")
plt.xlabel("Product ID")
plt.ylabel("Total Sales")

plt.show()