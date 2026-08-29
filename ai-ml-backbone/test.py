from classify import classify_and_route

result = classify_and_route(
    subject="Invoice discrepancy",
    body="My latest invoice shows the wrong amount, please help",
    language="en"
)
print(result)