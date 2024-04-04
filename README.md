# open-cosmos-backend-challenge


## Motivation

This service was created as part of the Open Cosmos backend challenge and addresses the following requirements:

- Fetch the data exposed by the server included as a binary with the project files.
- Store this data in a persistent data store; there are no requirements on which type of data store to use.
- Implement and apply the following business rules around the data:
  - Data whose timestamp is "too old" should be treated as invalid and discarded. "Too old" means the data are timestamped more than 1 hour previous to the current time.
  - The server does some basic analysis on the data and adds tags which both describe the data and possibly the outcomes of the analysis. Data internal to the system are tagged with "system" and should be discarded. If the server believes the data to be inaccurate, it will tag those data points with "suspect". Potentially inaccurate data should be discarded.
  - It must be possible for an administrator of the service, but not necessarily the end user of the service (/API), to discover which data points have been discarded and why they were discarded.
- Allow access to the stored data from the service with some filters described below: 
  - users must be able to access 
    - all data points 
    - data points generated after a certain datetime 
    - data points generated before a certain datetime 
    - data points generated within a set datetime range
- There are no requirements around the method of access.

## Run the Service

Before you run the service make sure you have ports 8000, 28462, and 27017 available in your system.
They will be used by the three different services of the main service.

For you to get the service up and running you need to:
1. clone this repository 
2. have docker up and running
3. Open a terminal window.
4. Open two tabs in that terminal window
5. In each tab of the terminal window navigate to the directory where you cloned the repository.
6. In one of the tab run the following command:
```bash
./start_data_server.sh
```

This will start the **data server** in port 28462.

If the message **Unable to start data server** appears make sure to manually run a different data server
on port 28462

7. In the other tab run the following command:
```bash
docker-compose up --build
```
This will start the FastAPI application in port 8000 and the MongoDB service used by the app in port 27017.
To make sure the app is up and running smoothly you should see the following message on the terminal: **Uvicorn running on http://0.0.0.0:8000**


You could run both commands, **./start_data_server.sh & docker-compose up --build**,  together however I advise you to run in separate tabs 
so you don't get the logs mixed up from both commands.


The service exposes two endpoints: 
- GET /data 
- GET /data_invalidation_reasons

For you to access those endpoints type http://localhost:8000/docs in the browser and you'll have access to Swagger.

**You'll need to provide an api_key in the headers of the request
to be able to use the endpoints.**


For the `GET /data` endpoint you can use "user_api_key" or "admin_api_key" as the api_key.  


For the `GET /data_invalidation_reasons` you can only use "admin_api_key". 
If you try to type "user_api_key" for this endpoint you'll get an error saying you have "Insuficient permissions"


For both endpoints you can also provide a `start_time` and/or an `end_time` to filter data.
These are optional parameters.
You should provide the start_time and the end_time in the following format: `YYYY-MM-DD hh:mm:ss`


## Service structure

The service uses the layered architecture pattern where you have:
- **Presentation Layer (API Layer)**: This layer defines the endpoints exposed to clients and handles HTTP requests and responses.

- **Business Logic Layer**: This layer contains the business rules and logic of the service. 
It receives requests from the API layer, processes them, and returns the appropriate responses. 
It communicates with the data storage layer to retrieve or manipulate data as needed.

- **Data Storage Layer (Infrastructure)**: This layer handles data storage and retrieval operations, 
interacting with databases or any other data storage mechanisms.

## The way the service works

When a user calls the **GET /data** endpoint it will do the following:
1. decorator **@fetch_data_from_server(business_logic)** is applied: 
It will fetch data from the data-server and store it in MongoDB. 
It will also check if there's any reasons to invalidate the data retrieved from the data-server
and if there is it will also store those reasons in MongoDB
2. decorator **@requires_permissions([READ_DATA_PERMISSION])** is applied:
It will check if the user that makes the request (provided by the api_key) has permissions
to get the data stored locally in MongoDB
3. If the user has permissions to get the data,
it will get the existent data stored in MongoDB and return it to the user

When a user calls the **GET /data_invalidation_reasons** endpoint it will do the following:
1. decorator **@fetch_data_from_server(business_logic)** is applied: 
It will fetch data from the data-server and store it in MongoDB. 
It will also check if there's any reasons to invalidate the data retrieved from the data-server
and if there is it will also store those reasons in MongoDB
2. decorator **@requires_permissions([VIEW_DATA_INVALIDATION_REASONS_PERMISSION])** is applied:
It will check if the user that makes the request (provided by the api_key) has permissions
to see why some data was eventually invalidated.
3. If the user has permissions to see the data invalidation reasons, this information is retrieved
from MongoDB and showed to the user. If not, it will appear the message **Insufficient permissions**

**Main Technical decisions**
- I decided not to have the service fetching data from the data-sever constantly.
This decision was made to avoid overloading the service with potential unnecessary requests.
And since the user of the service only needs to see the data when he/she calls the endpoint, 
there was only the need to have data available to retrieve in this situation.


- The fetching of the data from the data-server and the checking of the permissions to see the data
is done through **decorators** to make the code cleaner and easier to understand.


- An **AbstractDataStorage** class was created to make the business logic not to be dependent on any
specific data storage. This is because the business logic communicates directly with the 
data storage in use. The injection of the specific data storage to the business logic class
is done inside the BusinessLogicFactory class. This way someone can easily switch the data storage to be used.


- **MongoDB** was the choice for the data storage because of its simplicity to interact with 
using the available SDK to Python, pymongo. It is a persistent NoSQL database that is document-oriented
so it's perfect for this use case.


- As far as checking the permissions for accessing data, 
a simplified version of **Role-Based Access Control (RBAC)** method was used.
It is implemented with API key. The client should provide an api_key in the headers of 
the request


## Next Steps
As far as immediate next steps I would say:


1. **Enhance RBAC Implementation**: Consider changing the Role-Based Access Control (RBAC) implementation to a more secure and robust approach. In an ideal scenario, the `api_key` should be provided to the client upon login and then passed in subsequent requests through the header. It was assumed that the service of this repository would be integrated into a larger application where the login endpoint is implemented, allowing it to return an `api_key` for the user. Future improvements to the RBAC should take this into consideration to enhance security and access control mechanisms.

2. **Flexible Data Storage Configuration**: Explore the possibility of reading the data storage system configuration from environment variables. This would allow for the flexibility to use different data storage solutions depending on the environment in which this service is deployed. By decoupling the data storage configuration from the codebase, the service can easily adapt to various deployment environments without requiring code modifications.

