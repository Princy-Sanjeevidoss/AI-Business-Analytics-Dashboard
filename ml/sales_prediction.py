import pandas as pd
from sklearn.linear_model import LinearRegression

# Sample training data
data = {
    "Month": [1, 2, 3, 4, 5],
    "Sales": [10000, 12000, 15000, 17000, 19000]
}

df = pd.DataFrame(data)

# Features (X) and Target (y)
X = df[["Month"]]
y = df["Sales"]

# Create and train the model
model = LinearRegression()
model.fit(X, y)

# Predict sales for Month 6
prediction = model.predict([[6]])

print("Predicted Sales for Month 6:", prediction[0])