from setuptools import setup, find_packages
setup(
    name="fraud_detection",
    version="1.0.0",
    author="Elisha Pandey",
    description="Machine Learning project for Credit Card Fraud Detection",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "imbalanced-learn",
        "matplotlib",
        "seaborn",
        "jupyter",
        "python-dotenv"
    ],
    python_requires=">=3.11"
)