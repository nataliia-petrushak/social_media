# ShareHubAPI
ShareHub is a fictional API that was created to facilitate content sharing and social interactions among users within an online platform. Below is a description of the ShareHub API, including its features and functionality:

### ShareHub API Description:

#### User Management:

* Registration: Users can create accounts by providing a username, email, and password.
* Authentication: Users can log in using their credentials, and the API provides a token for authentication in subsequent requests.
* User Profile: Users can view and update their profile information, including names, profile pictures, and bio.

#### Posts:

* Create Posts: Authenticated users can create new posts, including text content and optional images.
* View Posts: Users can retrieve a list of posts, including their own and those shared by others.
* Post Details: Users can view the details of a specific post, including the author, content, and comments.
* Like and Unlike Posts: Users can like or unlike posts.
* Comments: Users can add comments to posts.
* Delete Posts: Post authors can delete their own posts. 

#### Hashtags:

* Create Hashtags: Users can create new hashtags to categorize and organize posts.
* Search Hashtags: Users can search for posts with specific hashtags.
* Hashtag Details: Users can view the details of a specific hashtag, including related posts.

#### Social Interactions:

* Follow and Unfollow Users: Users can follow or unfollow other users to see their posts.
* Followers and Following: Users can see a list of their followers and those they are following.

#### Scheduled Posts:

* Schedule Posts: Users can schedule posts for future publication.

#### Security and Permissions:

* Authentication: All API endpoints require authentication with a valid token.
* Authorization: Users can only perform actions on their own posts, comments or profiles.

### Installing using GitHub
Install PostgresSQL and create db

```shell
git clone https://github.com/nataliia-petrushak/social_media.git
cd social_media_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set POSTGRES_HOST=<your db hostname>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=secretpassword
=<your db password>
set SECRET_KEY=<your secret key>
```
### Run with docker
Docker should be installed

```shell
docker-compose build
docker-compose up
```

### Getting access
- create user via /api/user/register
- get access token via /api/user/token/

### Getting started
- Download [ModHeader](https://chrome.google.com/webstore/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en)
- Add name and token
- Now you are authorised and can use the API

### DB Structure
![DB Structure](https://drive.google.com/drive/u/0/my-drive)
