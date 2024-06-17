# social_network

## Introduction:
The app is mimics a simple social media app wherein you can sign up and log in, search for people and sent them friend requests.
You can also accept recieved friend request.

## How to launch the application.

### Step 1
Clone the repo into your local machine.

### Step 2
cd to root of this directory and run the following commands to create the image and run the container.
`docker-compose build`  
`docker-compose up`

### Step 3
Now go to your docker desktop and open the container created. You will see '8000' below your container hover over it to reveal the link and open it. You will see a django page not found error. That just means that your application is running and you can move over to the postman collection and try the apis.

## Apis:

### Import the postman collection SocialNetwork.postman_collection.

### `signup/`
**Method**- POST  
**Description** The api is used to create the new user. Set the Content-Type to application/json for all the apis. Go ahead and create a new user. Send the email and password in the body as json.

### `login/`
**Method**- POST  
**Description**-The api logins the user using his email and password to be sent in body.
The login api generates a access token and refresh token valid for 1 hr.
The token is generated using django's django-oauth-toolkit library.
Create one more user.

### `friends/`
**Method**- GET  
**Description**  
The api retruns all the friends of the user.
In headers set Authorization equal to Bearer `paste your access token recieved in login response`. This process needs to be done for all the apis except for signup and login.
Initially you will see empty list as response since you don't have any friends.

### `search/`
**Method**- GET  
**Description**  
The api returns the users that you search. You can search users based on their email or matching string to email. In the params, use key as `search` and value as email of the other user created. If you keep the value empty you will recieve all the users as response. Note the id of the user you want to send friend request to.

### `friend-request/send/`
**Method**- POST  
**Description**  
The api is used to send the friend request. Now paste the user id that you received in the response of 'search/' that you need to send the friend request to.
Send the id in body as `"to_user_id": "id_you_copied"`

### `friend-request/pending/`
**Method**- GET  
**Description**  The api is used to get all the pending requests. Now login with the user that you had send the friend request to. Now send this request. Do not forget to add authorization header with recieved access token.
You will see the pending friend request. Note the freind request id received as `id`.

### `friend-request/respond/<id>/accept`
**Method**- POST  
**Description**
The api is used to accept or reject the friend request. Now with the same user. Paste the id in the path to accept the request. And change the 'accept' in path to 'reject' to reject the request.


