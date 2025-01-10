# 🖥️ PICA'S COWORKING SPACE

<p align="center">
  Welcome to Pica's Coworking Space!
</p>

Pica's Coworking Space is a platform designed to enable users to book seats at coworking spaces easily. It features an integrated medicine recommendation system powered by MediMatch, enabling users to get suggestions for medicines to enhance their productivity while working.

---

## **Developer**
- **Name**: Firsa Athaya Raissa Alifah  
- **NIM**: 18222051  
- **Course**: II3160 Teknologi Sistem Terintegrasi  

---

## **Features**
1. **Authentication**: Users can sign up and log in to access the platform.  
2. **Reservations**: Book seats at coworking spaces for specific dates.  
3. **Medicine Recommendations**: Integrated with MediMatch to suggest medicines tailored to user needs.  

---

## **API Documentation**

### **Base URL**
- `Frontend`: Deployed via Vercel [coworkingspace-frontend](https://coworkingspace-six.vercel.app/)  
- `Backend`: Hosted on Railway [coworkingspace-backend](https://coworkingspace.up.railway.app/)  
- Full Documentation: [coworkingspace-API Docs](https://coworkingspace.up.railway.app/docs)

---

### **Endpoints**
#### **Authentication**
1. **Register User**
   - **Method**: `POST`
   - **Endpoint**: `/api/secure/register`
   - **Body (JSON)**:
     ```json
     {
       "username": "johndoe",
       "email": "johndoe@example.com",
       "password": "password123"
     }
     ```
   - **Response**:
     ```json
     {
       "message": "User registered successfully",
       "username": "johndoe"
     }
     ```

2. **Login User**
   - **Method**: `POST`
   - **Endpoint**: `/api/secure/login`
   - **Body (JSON)**:
     ```json
     {
       "username": "johndoe",
       "password": "password123"
     }
     ```
   - **Response**:
     ```json
     {
       "access_token": "<token>",
       "refresh_token": "<refresh_token>",
       "token_type": "bearer"
     }
     ```

#### **Reservations**
1. **Create Reservation**
   - **Method**: `POST`
   - **Endpoint**: `/api/secure/reservations`
   - **Headers**:
     - `Authorization`: Bearer `<token>`
   - **Body (JSON)**:
     ```json
     {
       "seat_number": "A1",
       "reservation_date": "2024-01-01"
     }
     ```
   - **Response**:
     ```json
     {
       "id": 1,
       "user_name": "johndoe",
       "seat_number": "A1",
       "reservation_date": "2024-01-01",
       "created_at": "2024-01-10T00:00:00Z"
     }
     ```

2. **Get All Reservations**
   - **Method**: `GET`
   - **Endpoint**: `/api/secure/reservations`
   - **Headers**:
     - `Authorization`: Bearer `<token>`
   - **Response**: List of reservations for the current user.

3. **Check Seat Availability**
   - **Method**: `GET`
   - **Endpoint**: `/api/secure/reservations/check-availability`
   - **Query Parameters**:
     - `seat_number`: The seat to check.
     - `reservation_date`: The date in `YYYY-MM-DD` format.
   - **Headers**:
     - `API-Key`: `<API_KEY>`

4. **Cancel Reservation**
   - **Method**: `DELETE`
   - **Endpoint**: `/api/secure/reservations/{reservation_id}`
   - **Headers**:
     - `Authorization`: Bearer `<token>`
   - **Response**:
     ```json
     {
       "message": "Reservation cancelled successfully"
     }
     ```

#### **Medicine Recommendation**
1. **Recommend Drugs**
   - **Method**: `POST`
   - **Endpoint**: `/api/secure/recommend-drugs`
   - **Headers**:
     - `API-Key`: `<API_KEY>`
   - **Body (JSON)**:
     ```json
     {
       "drug_name": "paracetamol",
       "top_n": 5
     }
     ```
   - **Response**:
     ```json
     {
       "data": {
         "1278": "Paracetamol 500mg",
         "1627": "Acetaminophen 500mg"
       }
     }
     ```

---

## **Technologies Used**
1. **Frontend**:
   - Built with HTML, CSS, and JavaScript.
   - Hosted on [Vercel](https://vercel.com/).
2. **Backend**:
   - Developed with FastAPI, running via `uvicorn`.
   - Hosted on [Railway](https://railway.app/).
   - Dockerized for consistent deployments.
3. **Database**:
   - Powered by [Supabase](https://supabase.com/) for scalable storage.
4. **Notifications**:
   - Handled via backend integration and frontend alerts.

---

## **Deployment**
1. **Frontend**:
   - Deployed on Vercel for high-speed performance and CI/CD integration.
2. **Backend**:
   - Deployed on Railway using Docker containers to ensure reliability and ease of scaling.
3. **Database**:
   - Hosted on Supabase for secure and efficient storage solutions.

---
