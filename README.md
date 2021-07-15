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
           
- `[GET] /api/user/info`  Get user info.
> User must be logged.
### User Pets
- `[GET] /api/user/pets` Get pets of a user.
> User must be logged.
 
- `[GET] /api/user/pets/<int:pet_id>` Get pet by id.
> User must be logged.

- `[POST] /api/user/pets/add` Add a pet to an user.
> User must be logged.
    
    JSON body must have this:

        {
            "name": "some name",
            "code_chip": "some code_chip",
            "breed": "some breed",
            "picture": "some picture",
            "birth_date": "some birth_date",
            "specie": "some specie"
        }
### User Pet History
- `[GET] /api/user/pet/<int:pet_id>/history` Get the history of a pet .
> User must be logged.

- `[POST] /api/user/pet/<int:pet_id>/history/vaccine/add` Add a vaccine to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "lot": "some lot",
            "name": "some name",
            "laboratory": "some laboratory"
        }
- `[POST] /api/user/pet/<int:pet_id>/history/diagnostic/add` Add a diagnostic to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "diagnostic": "some diagnostic",
            "doctor_name": "some doctor_name"
        }
- `[POST] /api/user/pet/<int:pet_id>/history/surgery/add` Add a surgery to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "description": "some description",
            "doctor_name": "some doctor_name"
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
- `[POST] /api/fundation/register` Register a foundation in the database.

    JSON body must have this data to register:
       
        {
            "email": "some email",
            "name": "some name",
            "address": "some address",
            "phone": "some number phone",
            "password": "some password"
        }
- `[POST] /api/fundation/login` Log in a foundation.
    >Foundation must be logged in
    
    JSON body must have this data:

        {
            "email": "some email",
            "password": "some password"
        }

- `[GET] /api/fundation/info` Return the foundation's info.
    >Foundation must be logged in

- `[GET] /api/fundation/pets` Return the foundation's pets.
    >Foundation must be logged in

- `[GET] /api/fundation/pets/<int:pet_id>` Return a specific foundation's pet.
    >Foundation must be logged in

- `[POST] /api/fundation/pets/add` Log in a foundation.
    >Foundation must be logged in
    
    JSON body must have this data:

        {
            "name": "A name", -> Required
            "specie": "cat" || "dog", -> Required
            "code_chip": "pet's code_chip" -> Optional
            "breed" : "pet's breed" -> Optional
            "picture": "pet's picture" -> Optional
            "birth" : "pet's birth date" -> Optional
        }

- `[POST] /api/fundation/transfer` Transfer a pet to an user.
    >Foundation must be logged in

    JSON body must have this data:

        {
            "email_user": "some email"
            "id_pet": number -> This id must be from a pet belonging    to the foundation
        }
