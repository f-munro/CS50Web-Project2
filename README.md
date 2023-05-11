# CS50 Web Development

## Project2 - Commerce

This is my submission for project 2 of the CS50 Web Development course. 
This project involved making an auction website in Django. 
Users either view all listings or browse by category. A use can also create 
their own listings, make bids, add to their wishlist and post comments.

I've tried to implement good form validation, on top of Django's already 
good validation, to make sure a user can't bid on their own items, and that only bids 
higher than the current price are valid. A user can close their own listings, and then
the highest bidder will be declared the winner.
