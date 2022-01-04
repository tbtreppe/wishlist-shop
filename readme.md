# Wishlist-Shop

## Introduction

Wishlist-Shop is a consumer driven webpage. The goal is to allow users to find and price out items they love. They will then be able to compile the items in one place - their Wishlist.

## Users

This site will be accesible for anyone who wants to create a wishlist of their most wanted items.

## Data

This webpage will use the [Google Shopping](https://rapidapi.com/ajmorenodelarosa/api/google-shopping/) API.

## Approach

Application will be built using Flask

#### Frontend

- Jinja
- Bootstrap
- Javascript

#### Backend

- postgreSQL
- Flask-SQLAlchemy
- Flask-Bcrypt

#### Hosting

Application will be hosted on Heroku

## Features

- Users will sign up and login in to be able to create and view their Wishlist page
- Users will be able to search for items using keywords
- Users will be able to click "Add" to any image and have it added to their Wishlist page
- Logged in users will be able to view and update their Wishlist page
  - Users will be able to delete any image they no longer want
  - Users will be able to add a check to something already bought

## Database Schema

[Schema](https://dbdiagram.io/d/61c68b1f3205b45b73cbfdd2)
