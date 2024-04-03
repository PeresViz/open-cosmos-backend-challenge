FROM python:3.9

# Create virtual environment
RUN python3 -m venv myenv

# Activate virtual environment
RUN . myenv/bin/activate

# Install dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app


# Run the data server and FastAPI application
CMD  python3 main.py
