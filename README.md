#Spotify Append 

##What it does
Spotify Append allows for playlists to have ***sources***™.  
A source is just a regular spotify playlist that your shiny new playlist tracks including any changes.     
Songs that you delete from your destination playlist do not automatically re-add. At a high level it's a bunch of playlists coming in and a filter removing certain known tracks.

##Example
Schema: 1,2 are sources, 3 is the destination (a - e are tracks)  
- 1 : {a,b} , 2 : {d, e} , 3 : {}  
- 3 will initially contain: {a,b,d,e} 
- user then deletes song a from 3 (song a)  
- 3:{b,d,e}  
- user adds c to 1:
- 1: {a,b,c} 3 : {b,c,d,e}
- user deletes d from 2
- 2: {e} (no change to 3)

The playlists are append only from the view of the sources. Removes are controlled entirely by the owner of the destination playlist

##How it does it
Frontend to backend is plain HTTP requests with JSON data  
Backend endpoints: auth, get and show all playlists, show and create drainlists  
Daily (or more often)run the sync.  
Currently the whole thing works but its rather messy. 

##Design Details
###Frontend endpoints are: 
1. add / remove source (local file changes only)
2. create / list drains (create is immediately followed by a populate, list is locals only )
3. list playlists (API call to get all playlists)  

###Backend:
1. everything is files (lots of manangemet with "open(a + b + c + d)" tons of places to go wrong)
2. temp playlists are written out to disk (needless)

##Moving Forward
- Currently we have a race condition if two sourced playlists use the same source there is only 1 copy meaning updates will only be applied to one destination.
    - In order to fix this, we can just have every destination list be in a self contained directory, do deduplication later. 
- Remove writing a reference out to disk so now we can do comparisons in memory, that's just lazy.
##Todo
1. Port to AWS (Lambda, S3, Dynamo)  
2. Account system
##Notes

 
