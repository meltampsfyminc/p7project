# How to Run the Tests

To verify the fix for the vehicle search functionality, please follow these steps:

1.  **Check your environment configuration:**
    *   Make sure you have a `.env` file inside the `property_management` directory.
    *   This file must contain the correct database connection details. An example is provided below:
        ```
        SECRET_KEY=your_secret_key
        DEBUG=True
        DB_ENGINE=django.db.backends.postgresql
        DB_NAME=your_db_name
        DB_USER=your_db_user
        DB_PASSWORD=your_db_password
        DB_HOST=localhost
        DB_PORT=5432
        ```

2.  **Install dependencies:**
    *   Make sure you have all the project dependencies installed.
    *   Open a terminal, navigate to the project root directory (`c:\Projects\p7project`), and run the following command:
        ```
        pip install -r property_management/requirements.txt
        ```

3.  **Run the tests:**
    *   Once the dependencies are installed, run the tests for the `vehicles` app using the following command:
        ```
        python property_management/manage.py test property_management.vehicles
        ```

If the tests run successfully, the search functionality is fixed.
