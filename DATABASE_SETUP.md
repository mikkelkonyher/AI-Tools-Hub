# Setting Up Your Own Database for AI Tools Hub

This guide will help you set up and run your own MongoDB database for the AI Tools Hub application.

## Table of Contents

1. [Setting Up MongoDB](#setting-up-mongodb)
2. [Configuring the Application](#configuring-the-application)
3. [Seeding the Database](#seeding-the-database)
4. [Verifying Your Setup](#verifying-your-setup)

## Setting Up MongoDB

### Using Docker (Recommended)

1. Start Docker Desktop application on your computer
2. Once Docker is running, execute this command:

```
docker run --name mongodb -d -p 27017:27017 -v mongodb_data:/data/db mongo:latest
```

This will:
- Create a container named "mongodb"
- Run MongoDB in the background
- Map port 27017 to your local machine
- Create a persistent volume for your data

You can verify it's running with:
```
docker ps | grep mongo
```

### Using MongoDB Atlas (Cloud Option)

If you prefer a cloud-hosted solution:

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Set up database access (create a user with password)
4. Set up network access (allow your IP address)
5. Get your connection string from the "Connect" button

## Configuring the Application

The application is already configured to use a local MongoDB instance. The connection settings are in the `backend/.env` file:

```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
```

To use your own database:

1. Make sure MongoDB is running (follow instructions above)

2. You can customize the database name by editing the `DB_NAME` value in `backend/.env`:

```
DB_NAME="my_ai_tools_db"
```

3. If you're using MongoDB Atlas or another hosted MongoDB service, update the `MONGO_URL` with your connection string:

```
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net"
```

4. Start the backend server which will connect to your database:

```
cd backend
python server.py
```

## Seeding the Database

The application is designed to automatically seed the database with sample AI tools data when it first runs.

### Automatic Seeding

1. When the frontend application loads, it calls the `seedData` function in `App.js` which makes a POST request to `/api/seed-data` endpoint.

2. The backend checks if there are any tools in the database. If the database is empty, it populates it with sample AI tools.

3. If data already exists, the seeding operation is skipped.

### Manual Seeding

You can also manually trigger the seeding process:

```
# Using curl
curl -X POST http://localhost:8000/api/seed-data
```

## Verifying Your Setup

After setting up your MongoDB database and configuring the application, you'll want to verify that everything is working correctly.

### Checking Database Connection

1. Start the backend server:
   ```
   cd backend
   python server.py
   ```

2. Look for a successful connection message in the console output.

### Verifying Data in the Database

#### Using MongoDB Compass (GUI Tool)

1. Download and install [MongoDB Compass](https://www.mongodb.com/products/compass)

2. Connect to your database:
   - For local MongoDB: `mongodb://localhost:27017`
   - For MongoDB Atlas: Use your connection string

3. Browse to your database (default is `test_database` or whatever you set in `.env`)

4. Check the collections:
   - `ai_tools` - Contains the AI tools data
   - `users` - Contains user accounts
   - `reviews` - Contains user reviews for tools

#### Using the API

You can also verify data through the API:

1. Start the frontend:
   ```
   cd frontend
   npm start
   ```

2. Open your browser to `http://localhost:3000`

3. If you see AI tools cards displayed, your database connection and data are working correctly.

## Troubleshooting

### Connection Issues

- Make sure MongoDB is running
- Check that the connection URL in `.env` is correct
- For MongoDB Atlas, ensure your IP is whitelisted

### Empty Database

- If no data appears, try manually seeding the database
- Check the backend logs for any errors during seeding

### Docker Issues

- If Docker container fails to start, try removing it and creating a new one:
  ```
  docker rm mongodb
  docker run --name mongodb -d -p 27017:27017 -v mongodb_data:/data/db mongo:latest
  ```