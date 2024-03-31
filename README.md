# SwiftSend API - SMS Platform for Digital Marketers

<a href="https://api-swift-send.koyeb.app/" style="display: flex; justify-content: center;">
    <img src="./assets/swiftsend figma.png" alt="swiftsend logo" style="width: 50%;"/>
</a>

Welcome to SwiftSend! This project is designed to provide a comprehensive platform for managing contacts, message templates, message logs, and recipient logs. SwiftSend offers a suite of features to help individuals and businesses stay connected with their contacts and streamline their messaging workflows. With intuitive API endpoints with robust functionality, my platform empowers users to:

-   Manage Contacts: Easily store, organize, and update contact information for individuals.
-   Create Templates: Craft reusable message templates to save time and ensure consistency in communication.
-   Send bult SMS to their contacts.
-   Track Message Logs: Keep a record of all sent messages, including delivery status and timestamps.
-   Resend or edit and resend an SMS from the logs.

## Features

-   **Contact Management:** Create, update, and delete contacts.
-   **Template Creation:** Design customizable message templates with dynamic placeholders for personalized content.
-   **Message Logging:** Record details of sent messages, including content, recipients, timestamps, and delivery status.
-   **Send Bulk SMS and Personalized templates to contacts at once.**
-   **Resend or Edit and Resend SMS from message logs.**

This project serves as a task as part of my recruitment process for a Backend Engineering role. It represents an opportunity for me to showcase my skills and expertise in developing backend solutions using Django, a powerful web framework for Python.

Throughout this project, I demonstrated my proficiency in various aspects of backend development, including:

1. **Database Design and Management**: Designing and implementing efficient database models to store and manage data effectively of which I used the <strong>`Postgres Database`</strong> from <a href="https://supabase.com/database">Supabase</a> a Cloud Database Plateform

2. **API Development**: I created robust APIs to facilitate communication between any SMS frontend and this backend application. Utilizing the <strong>`Django`</strong> and <strong>`Django Rest Framework`</strong>, I was able to achieve this with a few lines of code.

3. **Testing**: I wrote a comprehensive tests with the <a href="https://pypi.org/project/pytest-cov/">Pytest-Cov</a> library to ensure the reliability and stability of the backend codebase.

4. **Documentation**: With the help of the <a href="https://drf-spectacular.readthedocs.io/en/latest/readme.html">DRF-Spectacular</a> library, I was able to generate a clear and concise documentation to guide future developers and users of the system.

5. **Deployment**: Finally, I deployed the application to <a href="https://www.koyeb.com/">Koyeb</a> production environment, ensuring that it is secure, scalable, and accessible to end-users.

## Prerequisites

```
    python3.10
    django
    djanfo-restframework
    docker (*optional)
```

## Installation

1. #### Clone this repository

```
    git clone https://github.com/juliusmarkwei/ecommerce-backend.git
    cd ecommerce-backend/
```

2. #### Install all the neccessary packages/dependencies

```
    pip install -r requirements.txt
```

3. #### Environment Variables

-   Create a <strong>`.env`</strong>. Inside the <strong>.env</strong> add a <strong>`SECRET_KEY`</strong> and your database configurations of the database of your choice. You can generate a <strong>`SECRET_KEY`</strong> using the following code snippet:

```
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
```

-   Add the following line printed above to the <strong>`.env`</strong> file:

```
    SECRET_KEY=your_secret_key_here

    DB_HOST=your_db_host
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_NAME=your_db_name
    DB_PORT=your_db_port
    DB_ENGINE=your_db_engine

    EMAIL_BACKEND=your_email_backend
    EMAIL_HOST=your_email_host
    EMAIL_PORT=your_email_port
    EMAIL_HOST_USER=your_email_user
    EMAIL_HOST_PASSWORD=your_email_password

    AFRICASTALKING_API_KEY=your_api_key
    AFRICASTALKING_USERNAME=your_username
```

3. #### Confguring Database Admin User
    In the root directory of the project, create a superuser to manage all the users of the application. be sure python is installed before you proceed with this stage.

```
    python3 manage.py createsuperuser
```

4. #### Starting the server and Access the Application

-   Run the command below to start the application server and access the application running on a default port 8000 via http://localhost:8000.

```
    python3 manage.py runserver
```

<img src="./assets/play.svg" width=15px heigth=15px> Enjoy SwiftSend

## Get Involved

We welcome contributions and participation from the community to help make this e-commerce backend API even better! Whether you're looking to fix bugs, add new features, or improve documentation, your help is greatly appreciated. Here's how you can get involved:

### Reporting Issues 🚩

If you encounter any bugs or issues, please report them using the <a href="https://github.com/juliusmarkwei/swift-send/issues"> Issues</a> section of my GitHub repository. When reporting issues, please include:

-   A clear and descriptive title.
-   A detailed description of the problem, including steps to reproduce it.
-   Any relevant logs or error messages.
    Your environment details (e.g., Django version, DRF version, database, etc.).

### Contributing Code <img src="./assets/collaboration.svg" width="19px" heigth="19px">

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix: git checkout -b feature-branch.
3. Make your changes and commit them: git commit -m 'Add new feature'.
4. Push to the branch: git push origin feature-branch.
5. Submit a pull request with a detailed description of your changes.
