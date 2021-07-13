# App-backend
## Rules
  - Modificar sobre ramas y pedir pull request

  - Usar snake_case

  - Usar nombres en ingles
## API endpoints
- `[GET] /` is a Test endpoint
### User 
- `[POST] /user/register` Register an user in the database.

    JSON body must have this data to register an user:
      
      {
          "email": "some email",
          "name":"some name",
          "lastname":"some lastname",
          "password": "some password"
      }
- `[POST] /user/login` Log in a user.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }
### Clinic
- `[POST] /clinic/register` Register a clinic in the database.

    JSON body must have this data to register a clinic:

      {
          "email": "some email",
          "name": "some name",
          "address": "some address",
          "phone": "some phone",
          "password": "some password"
      }
- `[POST] /clinic/login` Log in a clinic.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }
### Doctors
- `[POST] /doctor/register` Register a doctor in the database.
    JSON body must have this data to register a doctor:

      {
          "email": "some email",
          "name": "some name",
          "lastname": "some lastname",
          "speciality": "some speciality"
          "password": "some password"
      }
- `[POST] /doctor/login` Log in a doctor.

    JSON body must have this data :

      {
          "email": "some email",
          "password": "some password"
      }
### Fundations
- `[POST] /fundation/register` Register a doctor in the database.

    JSON body must have this data to register:
       
        {
            "email": "some email",
            "name": "some name",
            "lastname": "some lastname",
            "speciality": "some speciality",
            "password": "some password"
        }
- `[POST] /fundation/login` Log in a fundation.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }

