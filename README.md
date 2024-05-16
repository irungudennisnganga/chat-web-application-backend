# chat-web-application-backend

This project is based on a making communication easier by simply sending messages
to people you are connected with.

## Introduction

This documentation is made for (Dennis Irungu) and other developers to have the whole idea of the
do and dont's of my API, the things that are provided by the API, the endpoints, data type that are
supported at the server and the relationship between all the models and how they work.

## TABLE OF CONTENT

(Add table of content here !!)

## MVP

1. As a user i can create my chat-web account and verify my account via an OTP pin that is send to my email
2. As a user i can login/log out of my account
3. As a user i can send a message to another user
4. As a user i can update my account details

### FUTURE UPDATES

1. As a user i can add a status that is veiwed by other users
2. As a user i can create my account using my google account  -- (check later)
3. As a user i can make a call with another user who we are connected with

## INSTALLATION

For Linux users head to your terminal and enter the directory where you want to clone your
project using this command,

``` bash
    cd directory-name
```

After that take the SSH or Https link in github to clone the project using this command

```bash
    git clone giyhub-link
```

Open the project in your IDM for me i am using VSCode so i'll run this command to open the
project on my Linux terminal

```bash
    code directory-name
```

After opening the project successfully, open the VSCode terminal (ctr + ` ) and create a branch where You will
work on using the following commands

1. Swith the branch from main to develop

```bash
    git checkout develop
```

This command will install all the dependency that are required to run the application

```bash
    pipenv install
```

Enter to the enviroment that has been created by installing the dependecy above

```bash
    pipenv shell
```

To run the application use this code

```bash
    python app.py
```

Open another terminal to run this  commands

2. The command below will initialize git init to the project

```bash
    git flow init
```

3. Create a feature where by you will work on each feature

```bash
    git flow start feature feature_name
```

4. After working on the feature and want to push the code follow this proccess

```bash
    git add .
```

```bash
    git commit -m "message"
```

```bash
    git push feature_name
```

5. Run this command to mearge the feature and delete the branch from the local
    and remote repository

```bash
    git flow stop feature feature_name
```

Congratulation you have been able to push your code for reviewing

## API ENDPOINTS AND ALL IT'S DETAILS

### 1. UserData --  "/create_account"

This is a <B>POST</B> request that takes 5 arguments brokend down as follows:

i. username -- string (required)

ii. phone_number -- integer (required)

iii. email -- email (required)

iv. profile_picture -- image (not a must)

v. password -- password (required)

After taking the arguments as expected the server will generate an OTP pin that is send to the user's email
to verify the account before accessing anything from the server
The otp generated is stored along with the user's data after creating an account. The verifying proccess it handled by another route
as follows below

### 2. VerifyOTP --  "/verify_otp"

This is a <b>POST</b> request that takes in 2 arguments as shown below:

i. phone_number -- integer (required)

ii. otp -- otp (required)

In this request the phone number is taken and then it is used to make a fetch request to fetch the user that matches with
the phone number provided, after getting the user, remember we stored the otp that was generated and sent to the user in our
server, we need to verify if the otp provided by the user matches the otp that was stored to our server

If <b><i>true</i></b> update the user status from "inactive" to "active" else return "OTP is incorrect"

### 3. Login --  "/login"

This is a <b>POST</b> request that takes in 2 arguments as follows:

i. email -- email (required)

ii. password -- password (required)

<b>If</b> email and password are not provided return {"message": "Please enter Email and Password to continue"}

After getting the email and the password, a get request is made to the user table to get the user associated with the email
provided above.

<b>If</b> no user is found  return {"message": "Wrong credentials"}

After finding the user associated with the email take the hashed password and check aganist the password provided by the user

<b>If</b> <b><i>true</i></b> create access token and return the access token <b><i>else</i></b> return {"message": "Wrong password"}

### 4. CheckSession -- "/check_session"

This is a protected <b>GET</b> request that gets the user's identity using jwt tools and makes a get request to
the users table to get the user based on the id 

<b>If</b> no user is found return {"message": "user not found"} <b><i>else</i></b> return user's data 

        {

            "user_id": user.id,

            "username": user.useername,

            "email": user.email,

            "contact": user.contact, 

        }