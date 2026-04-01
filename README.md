# Task-Progress-Tracking-System
🚀 Task Progress Tracking & Management Portal
A robust, full-stack Task Management System built with Streamlit and MongoDB. This application provides a centralized dashboard for Admins, Managers, and Employees to track productivity, assign tasks, and visualize performance analytics in real-time.

✨ Key Features
👤 Multi-Role Access Control
Admin: Full CRUD (Create, Read, Update, Delete) capabilities over tasks.

Management: Supervisory access to monitor team progress and provide feedback.

Employee: Personalized view to track assigned tasks and submit status updates.

📊 Real-Time Analytics
Interactive Charts: Utilizes Plotly to generate dynamic pie charts and grouped bar graphs.

Automated Status Logic: Automatically categorizes tasks as "Completed," "In Progress," or "Past Due" based on submission dates and keywords.

Timeline Summary: Visualizes task distribution over months to identify productivity trends.

🛠️ Tech Stack
Frontend: Streamlit

Database: MongoDB Atlas

Data Manipulation: Pandas

Visualization: Plotly

🚀 Getting Started
1. Prerequisites
Ensure you have Python 3.9+ installed. You will also need a MongoDB Atlas cluster.

2. Installation
Clone the repository and install the required dependencies:

Bash
pip install streamlit pandas pymongo plotly
3. Database Configuration
The system connects to a MongoDB database named Company_MIS with two primary collections:

4. Running the Application
Bash
streamlit run "Task Progress Tracking System.py"

User_Auth: Stores credentials (user_id, password, role).

Employee_Data: Stores task details and employee records.
