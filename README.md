# Dynamic Tables

Simple backend for a table builder app, where the user can build tables dynamicaly.
The app has the following endpoints:

- **POST**  `/api/table`    Generate dynamic Django model based on user provided fields types and titles. The field type can be a string, number, or Boolean.
- **PUT**   `/api/table/:id` This end point allows the user to update the structure of dynamically generated model.
- **POST** `/api/table/:id/row` Allows the user to add rows to the dynamically generated model while respecting the model schema
- **GET** `/api/table/:id/rows` Get all the rows in the dynamically generated model
