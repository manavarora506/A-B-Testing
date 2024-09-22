# A/B Testing Contact Form Project

This project implements an A/B testing system for evaluating changes in contact form submission behavior on two different sites, Site A and Site B. The system tracks metrics such as form submissions and visits for each site, allowing for a dynamic, admin-controlled frontend configuration for Site B.

## Features

- **A/B Testing**: Users are randomly directed to either Site A or Site B based on a configurable routing probability.
- **Dynamic Form Configurations**: The admin can update form fields, styles, and images for Site B via a configuration panel.
- **Real-time Metrics**: Track visits and form submissions on both Site A and Site B.
- **Difference Tracking**: Automatically records differences in form fields, styles, and images between Site A and Site B when a form is submitted.
- **Admin Panel**: Allows real-time configuration and adjustment of Site B's form, routing probability, and more.

## Technologies

- **Backend**: FastAPI (Python)
- **Frontend**: React (JavaScript), Material UI
- **Database**: MongoDB (for storing form submissions and configuration)
- **Styling**: Material UI (for admin panel and frontend form)
- **A/B Testing**: Admin can control form fields and styles for Site B while Site A serves as the control site.

## Setup and Installation

### Prerequisites

- Python 3.9+
- Node.js and npm (for the frontend)
- MongoDB instance

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/ab-testing.git
   cd ab-testing

### Backend Setup

1. **Activate Environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # For Linux/macOS
    .\env\Scripts\activate   # For Windows

2. Create a .env file in the root directory and add your MongoDB URI:
    ```touch .env```

3. Inside the .env file, add:
    ```MONGO_URL=mongodb+srv://your_username:your_password@cluster0.mongodb.net/dbname```

4. **Run the backend**:
    ```uvicorn main:app --reload```

### Frontend Setup

1. **Navigate to the frontend directory**:
    ```bash
    cd frontend

2. **Install dependencies**:
    ```bash
    npm install

3. **Run the frontend**:
    ```bash
    npm start

### MongoDB Setup

Set up a MongoDB instance and create two collections:

- **form_submissions**: To store form submissions from both Site A and Site B.
- **form_config**: To store the dynamic configuration for Site B.

### Usage

- Access the backend API at [http://localhost:8000](http://localhost:8000) for testing or API calls.
- Access the frontend (Site A and Site B) at [http://localhost:3000](http://localhost:3000).
- Use the admin panel to configure Site B's form at `/admin`.

### API Endpoints

- **Route User**: `/route` (GET)  
  Directs users to either Site A or Site B based on the routing probability.

- **Admin - Get Form Config**: `/admin/form-config` (GET)  
  Retrieves the current configuration for Site B's form.

- **Admin - Update Form Config**: `/admin/save-form-config` (PUT)  
  Saves a new form configuration for Site B.

- **Admin - Update Routing Probability**: `/admin/update-routing-probability` (PUT)  
  Updates the routing probability between Site A and Site B.

- **Form Submission (Site A)**: `/submit-form/site-a` (POST)  
  Submit the form data for Site A.

- **Form Submission (Site B)**: `/submit-form/site-b` (POST)  
  Submit the form data for Site B. Dynamically validates the form based on the Site B configuration.

- **Get Metrics**: `/metrics` (GET)  
  Retrieves metrics on visits and form submissions for both Site A and Site B, along with differences in fields, styles, and images between Site A and Site B.

### A/B Testing Flow

1. When a user accesses the form page, they are randomly directed to either Site A or Site B.
2. Site A serves a static contact form, while Site B dynamically pulls its configuration from the admin settings.
3. Admins can update form fields, styles, and images for Site B and observe the metrics.
4. Form submissions for both sites are stored in MongoDB with metrics tracked in real-time, and any differences in fields, styles, or images between Site A and Site B are saved in the database.

### Environment Variables

- **MONGO_URL**: MongoDB connection string. Add this in your `.env` file.

### License

This project is licensed under the MIT License. See the LICENSE file for details.
