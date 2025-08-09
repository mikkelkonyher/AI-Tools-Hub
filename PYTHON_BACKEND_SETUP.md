# Running the Python Backend for AI Tools Hub

This guide will help you set up and run the Python backend for the AI Tools Hub project.

## Prerequisites

- Python 3.8 or higher
- MongoDB (see [DATABASE_SETUP.md](DATABASE_SETUP.md) for database setup)
- pip (Python package manager)

## Setting Up the Python Environment

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   
   # On Windows
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Backend Server

1. Make sure your MongoDB is running (see [DATABASE_SETUP.md](DATABASE_SETUP.md))

2. Start the backend server using uvicorn:
   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

   This command:
   - Runs the FastAPI application defined in `server.py`
   - Enables auto-reload for development
   - Makes the server accessible from other devices on your network
   - Uses port 8000

3. The backend should now be running at `http://localhost:8000`

4. You can access the API documentation at `http://localhost:8000/docs`

## IDE Options

### Using WebStorm

WebStorm is primarily a JavaScript/TypeScript IDE, but it can run Python scripts with the proper configuration:

1. Install the "Python Community Edition" plugin in WebStorm
2. Configure the Python interpreter (point to your virtual environment)
3. Create a run configuration:
   - Type: Python
   - Script path: Path to uvicorn in your virtual environment
   - Parameters: `server:app --reload --host 0.0.0.0 --port 8000`
   - Working directory: Your backend directory

However, WebStorm's Python support is limited compared to dedicated Python IDEs.

### Using PyCharm (Recommended for Backend)

PyCharm provides better support for Python development:

1. Open the backend directory in PyCharm
2. Configure the Python interpreter (point to your virtual environment)
3. Create a run configuration:
   - Type: Python
   - Script path: Path to uvicorn in your virtual environment
   - Parameters: `server:app --reload --host 0.0.0.0 --port 8000`
   - Working directory: Your backend directory

PyCharm offers better debugging, code completion, and inspection for Python code.

## Development Workflow

For the best development experience:

- Use PyCharm for backend development (Python)
- Use WebStorm for frontend development (React)
- Run both servers simultaneously during development

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

2. **MongoDB connection errors**: Ensure MongoDB is running and check the connection string in `.env`

3. **Port already in use**: If port 8000 is already in use, change the port number in the uvicorn command

4. **Environment variables not loading**: Make sure your `.env` file is properly configured in the backend directory