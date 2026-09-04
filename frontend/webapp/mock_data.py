"""Static reference data still used by the frontend (queue list, accents).
Message fixtures have been removed - the app now reads real data from the backend API."""

QUEUES = [
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
]

QUEUE_ACCENTS = {
    "Billing and Payments": "amber",
    "Customer Service": "teal",
    "General Inquiry": "slate",
    "Human Resources": "plum",
    "IT Support": "cyan",
    "Product Support": "indigo",
    "Returns and Exchanges": "rose",
    "Sales and Pre-Sales": "green",
    "Service Outages and Maintenance": "red",
    "Technical Support": "blue",
}