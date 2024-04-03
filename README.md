# open-cosmos-backend-challenge


## Motivation

This service was created as part of the Open Cosmos backend challenge and addresses the following requirements:

- Fetch the data exposed by the server included as a binary with the project files.
- Store this data in a persistent data store; there are no requirements on which type of data store to use.
- Implement and apply the following business rules around the data:
  - Data whose timestamp is "too old" should be treated as invalid and discarded. "Too old" means the data are timestamped more than 1 hour previous to the current time.
  - The server does some basic analysis on the data and adds tags which both describe the data and possibly the outcomes of the analysis. Data internal to the system are tagged with "system" and should be discarded. If the server believes the data to be inaccurate, it will tag those data points with "suspect". Potentially inaccurate data should be discarded.
  - It must be possible for an administrator of the service, but not necessarily the end user of the service (/API), to discover which data points have been discarded and why they were discarded.
- Allow access to the stored data from the service with some filters described below; there are no requirements around the method of access.

## Run the Service

For you to get the service up and running you need to:
1. clone this repository 
2. have docker up and running
3. Open a terminal window.
4. Navigate to the directory where you cloned the repository.
5. Run the following command:
```bash
./start_data_server.sh & docker-compose up --build
```

The service exposes two endpoints: 
- GET /data 
- GET /data_invalidation_reasons

For you to access those endpoints type http://localhost:8000/docs in the browser and you'll have access to Swagger.

You'll need to provide an api_key to be able to use the endpoints. For the GET /data endpoint you can use "user_api_key" or "admin_api_key" as the api_key.  For the GET /data_invalidation_reasons you can only use "admin_api_key". If you try to type "user_api_key" for this endpoint you'll get an error saying you have "Insuficient permissions"


## Service structure

The service uses the layered architecture pattern where you have:
- **Presentation Layer (API Layer)**: This layer defines the endpoints exposed to clients and handles HTTP requests and responses.

- **Business Logic Layer**: This layer contains the business rules and logic of the service. 
It receives requests from the API layer, processes them, and returns the appropriate responses. 
It communicates with the data storage layer to retrieve or manipulate data as needed.

- **Data Storage Layer (Infrastructure)**: This layer handles data storage and retrieval operations, 
interacting with databases or any other data storage mechanisms.

## The way the service works

The service uses the layered architecture pattern where you have:
- **Presentation Layer (API Layer)**: This layer defines the endpoints exposed to clients and handles HTTP requests and responses.

- **Business Logic Layer**: This layer contains the business rules and logic of the service. 
It receives requests from the API layer, processes them, and returns the appropriate responses. 
It communicates with the data storage layer to retrieve or manipulate data as needed.

- **Data Storage Layer (Infrastructure)**: This layer handles data storage and retrieval operations, 
interacting with databases or any other data storage mechanisms.

## Next Steps

Some potential next steps for this project include:

- Improving the efficiency and scalability of the data storage and retrieval processes.
- Enhancing the analysis capabilities to provide more insightful tagging and categorization of data.
- Implementing additional security measures to protect sensitive data and ensure secure access.
- Enhancing the user interface for easier administration and data retrieval.

