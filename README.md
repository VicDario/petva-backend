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

        returns:    409 if the email already exists
                    201 if the user was created           

- `[POST] /api/user/login` Log in a user.

    JSON body must have this data:

        {
            "email": "some email",
            "password": "some password"
        }

        returns:    401 if email or password is not correct.
                    201 if user is logged in.
           
- `[GET] /api/user/info`  Get user info.
> User must be logged.

- `[PUT] /api/user/info`  Modify user info.
> User must be logged.
    JSON body must have this data:
        {
            "email": "some email",
            "name":"some name",
            "lastname":"some lastname",
            "phone": "some phone",
            "picture": "some picture", -> Optional -> if not provided, the picture will not be modified -> send null
            "password": "some password" -> Optional -> if not provided, the password will not be modified -> send null
        }

        return: 202 if info was modified.
### User Pets
- `[GET] /api/user/pets` Get pets of a user.
> User must be logged.

        returns:    200 with a list of pets

- `[GET] /api/user/pets/<int:pet_id>` Get pet by id.
> User must be logged.

        returns:    200 if the pet was found with its info.
                    404 if the pet was not found

                    
- `[PUT] /api/user/pets/<int:pet_id>` Modify pet by id.
> User must be logged.

    JSON body must have this:

        {
            "name": "some name",
            "code_chip": "some code_chip",
            "breed": "some breed",
            "picture": "some picture"
        }

        returns:    202 if the info was modified.
                    404 if the pet was not found

- `[DELETE] /api/user/pets/<int:pet_id>` Delete pet by id.
> User must be logged.

    JSON body must have this:

        returns:    203 if the pet was deleted.
                    404 if the pet was not found.
                    409 if the pet is part of a foundation, cannot be deleted.

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

        returns:    201 if the pet was added

- `[POST] /api/user/pets/<int:pet_id>/report/lost` Report a pet how lost.
> User must be logged.

    JSON body must have this:

        {
            "last_location": "some last_location",
        }

- `[GET] /api/user/pets/<int:pet_id>/report/founded` Report a pet how founded.
> User must be logged.

### User Pet History
- `[GET] /api/user/pets/<int:pet_id>/history` Get the history of a pet.
> User must be logged.
        returns:    200 if the pet was found
                    404 if the pet was not found

- `[POST] /api/user/pets/<int:pet_id>/history/vaccine/add` Add a vaccine to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "lot": "some lot",
            "name": "some name",
            "laboratory": "some laboratory"
        }

        returns:   201 if the vaccine was added

- `[POST] /api/user/pet/<int:pet_id>/history/diagnostic/add` Add a diagnostic to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "diagnostic": "some diagnostic",
            "doctor_name": "some doctor_name"
        }

        returns:   201 if the diagnostic was added

- `[POST] /api/user/pet/<int:pet_id>/history/surgery/add` Add a surgery to history of a pet.
> User must be logged.

    JSON body must have this:

        {
            "date": "some date",
            "description": "some description",
            "doctor_name": "some doctor_name"
        }

        returns:   201 if the surgery was added
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

        returns:    409 if the email already exists
                    201 if the clinic was created

- `[POST] /api/clinic/login` Log in a clinic.

    JSON body must have this data:

        {
            "email": "some email",
            "password": "some password"
        }

        returns:    401 if email or password is not correct.
                    201 if clinic is logged in.

- `[GET] /api/clinic/info` Get clinic info.
> Clinic must be logged.

        returns:    200 with the clinic info

- `[PUT] /api/clinic/info` Modify clinic info.  // TODO Create this route

- `[GET] /api/clinic/check/reserved` Get reservations.
> Clinic must be logged.

        returns:    200 with a list of reservations
### Doctors
- `[POST] /api/clinic/doctor/register` Register a doctor in the database.
> Clinic must be logged.
    JSON body must have this data to register a doctor:

        {
            "email": "some email",
            "name": "some name",
            "lastname": "some lastname",
            "speciality": "some speciality"
            "password": "some password"
        }

        returns:    409 if the email already exists
                    201 if the doctor was created
    
-`[DELETE] /api/clinic/doctor/<int:id_doctor` Delete a doctor.
> Clinic must be logged.

- `[POST] /api/doctor/login` Log in a doctor.

    JSON body must have this data :

        {
            "email": "some email",
            "password": "some password"
        }

        returns:    401 if email or password is not correct.
                    201 if the doctor was logged in.

-`[GET] /user/clinics/<int:clinic_id>/doctor/<int:doctor_id>/reservation/add` Add a reservation to a doctor.
> Doctor must be logged.

    JSON body must have this data:
        {
            "id_pet": "some id_pet",
        }


### Doctors

-`[POST] /doctor/reservations/add` Open a reservation.
> Doctor must be logged.
    JSON body must have this data:
        {
            "hour_start": "some hour_start", -> Format ISO
            "hour_end": "some hour_end", -> Format ISO
        }

### Fundations
- `[POST] /api/foundation/register` Register a foundation in the database.

    JSON body must have this data to register:
       
        {
            "email": "some email",
            "name": "some name",
            "address": "some address",
            "phone": "some number phone",
            "password": "some password"
        }

    returns:    409 if the email already exists
                201 if the fundation was created

- `[POST] /api/foundation/login` Log in a foundation.
>Foundation must be logged in
    
    JSON body must have this data:

        {
            "email": "some email",
            "password": "some password"
        }

        returns:    401 if email or password is not correct.
                    201 if the foundation was logged in.

- `[GET] /api/foundation/info` Return the foundation's info.
>Foundation must be logged in

        returns:    200 with the foundation's info

- `[PUT] /api/foundation/info`  Modify user info.
> Foundation must be logged.

    JSON body must have this data:
        {
            "email": "some email",
            "name":"some name",
            "address":"some address",
            "phone": "some phone",
            "picture": "some picture", -> Optional -> if not provided, the picture will not be modified -> send null
            "password": "some password" -> Optional -> if not provided, the password will not be modified -> send null
        }

        return: 202 if info was modified.

- `[GET] /api/foundation/pets/in_adoption` Return the foundation's pets in adoption.
>Foundation must be logged in

        returns:    200 with the pets in adoption

- `[GET] /api/foundation/pets/owned` Return the foundation's pets with owner for tracking.
>Foundation must be logged in

        returns:    200 with the pets with owner for tracking

- `[GET] /api/foundation/pets/<int:pet_id>` Return a specific foundation's pet.
>Foundation must be logged in

        returns:    200 with the pet
                    404 if the pet was not found

- `[POST] /api/foundation/pets/add` Log in a foundation.
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

        returns:    201 if the pet was added

- `[POST] /api/foundation/transfer` Transfer a pet to an user.
>Foundation must be logged in

    JSON body must have this data:

        {
            "email_user": "some email"
            "id_pet": number -> This id must be from a pet belonging to the foundation
        }

        returns:    201 if the pet was transferred
                    404 if the pet or user were not found

- `[GET] /api/foundation/pets/<int:pet_id>/history` Get the history of a pet.
    >Foundation must be logged in

        returns:    200 if the pet was found
                    404 if the pet was not found

- `[POST] /api//foundation/pets/<int:pet_id>/history/vaccine/add` Add a vaccine to history of a pet.
>Foundation must be logged in

    JSON body must have this data:

        {
            "date": "some date",
            "lot": "some lot",
            "name": "some name",
            "laboratory": "some laboratory"
        }

        returns:    201 if the vaccine was added
                    404 if the pet was not found
                
- `[POST] /api/foundation/pets/<int:pet_id>/history/diagnostic/add` Add a diagnostic to history of a pet.
>Foundation must be logged in

    JSON body must have this data:

        {
            "date": "some date",
            "diagnostic": "some diagnostic",
            "doctor_name": "some doctor_name"
        }

        returns:    201 if the diagnostic was added
                    404 if the pet was not found

- `[POST] /api/foundation/pets/<int:pet_id>/history/surgery/add` Add a surgery to history of a pet.
>Foundation must be logged in

    JSON body must have this data:

        {
            "date": "some date",
            "description": "some description",
            "doctor_name": "some doctor_name"
        }

        returns:    201 if the surgery was added
                    404 if the pet was not found

- `[GET] '/api/pets/in_adoption/<int:page>'` Gets pets in adoption with all info necessary. 10 pets per page.

    returns:  {pets(array), number_of_pages(int), page_has_next(Boolean), page_has_previous(Boolean)}, 200

- `[GET] '/api/pets/lost/<int:page>'` Gets lost pets with all info necessary. 10 pets per page.

    returns:  {pets(array), number_of_pages(int), page_has_next(Boolean), page_has_previous(Boolean)}, 200
