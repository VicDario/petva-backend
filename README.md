# App-backend
## Rules
  - Modificar sobre ramas y pedir pull request

  - Usar snake_case

  - Usar nombres en ingles
## API endpoints
- `[GET] /` is a Test endpoint
### User 
- `[POST] /api/user/register` Register an user in the database.

    JSON body must have this data to register an user:
      
      {
          "email": "some email",
          "name":"some name",
          "lastname":"some lastname",
          "password": "some password"
      }
- `[POST] /api/user/login` Log in a user.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }
### Clinic
- `[POST] /api/clinic/register` Register a clinic in the database.

    JSON body must have this data to register a clinic:

      {
          "email": "some email",
          "name": "some name",
          "address": "some address",
          "phone": "some phone",
          "password": "some password"
      }
- `[POST] /api/clinic/login` Log in a clinic.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }
### Doctors
- `[POST] /api/doctor/register` Register a doctor in the database.
    JSON body must have this data to register a doctor:

      {
          "email": "some email",
          "name": "some name",
          "lastname": "some lastname",
          "speciality": "some speciality"
          "password": "some password"
      }
- `[POST] /api/doctor/login` Log in a doctor.

    JSON body must have this data :

      {
          "email": "some email",
          "password": "some password"
      }
### Fundations
- `[POST] /api/fundation/register` Register a doctor in the database.

    JSON body must have this data to register:
       
        {
            "email": "some email",
            "name": "some name",
            "lastname": "some lastname",
            "speciality": "some speciality",
            "password": "some password"
        }
- `[POST] /api/fundation/login` Log in a fundation.

    JSON body must have this data:

      {
          "email": "some email",
          "password": "some password"
      }

