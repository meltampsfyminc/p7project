# How to Apply the Database Migrations

To apply the database changes for the new occupant and housing unit features, please follow these steps:

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

3.  **Create the migrations:**
    *   After installing the dependencies, run the following command to create the migration files for the `properties` app:
        ```
        python property_management/manage.py makemigrations properties
        ```
    *   This will create a new migration file in the `property_management/properties/migrations` directory.

4.  **Apply the migrations:**
    *   Finally, apply the migrations to your database by running the following command:
        ```
        python property_management/manage.py migrate properties
        ```

If the migrations run successfully, the new database schema will be applied.
After that, you should be able to use the new features for managing housing units and occupants.
