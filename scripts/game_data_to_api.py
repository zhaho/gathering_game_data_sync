import xmltodict, json
import requests
import time
import logging
# import ast
# from operator import itemgetter
logging.basicConfig(filename='/var/log/bgg.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def push_data(games):
    # Set headers for post
    headers = {"Content-Type": "application/json"}

    # Loop the list
    for obj in games:
        object_id = obj['object_id']
        print(object_id)

        # Get info about game from BGG API
        response = requests.get("https://boardgamegeek.com/xmlapi/boardgame/"+object_id+"?stats=1") # Get information of game through BGG API
        dictionary = xmltodict.parse(response.content) # Parse the XML to Dict
        json_object_string = json.dumps(dictionary) # Convert to String
        json_object = json.loads(json_object_string) # Convert JSON to LIST

        #print(json_object)
        # Sort out information
        # categories = json_object['boardgames']['boardgame']['boardgamecategory']
        # category = ""
        # for cat in categories: 
        #     category += cat['#text'] + ", "

        # #preferred_players
        
        # mechanics = json_object['boardgames']['boardgame']['boardgamemechanic']
        # mechanic = ""
        # for mech in mechanics:
        #     mechanic += str(mech['#text'] + ", ")
        

        # Sets the title 
        title_object = json_object['boardgames']['boardgame']['name']
        # Check if it has 2 or more keys
        for obj in title_object:
            try:
                obj_len = len(obj.keys())
            except:
                title = json_object['boardgames']['boardgame']['name']['#text']
                obj_len = 0
           
            if obj_len > 2:
                title = obj['#text']

        # Sets the category
        category = " "
        if 'boardgamecategory' in  json_object['boardgames']['boardgame']:
            category_object = json_object['boardgames']['boardgame']['boardgamecategory']
            for obj in category_object:
                try:
                    category += obj['#text']+ ", "
                except:
                    category = json_object['boardgames']['boardgame']['boardgamecategory']['#text']

            category_length = len(category)
            category = category[0:category_length-2]
        
        # Sets the mechanic
        mechanic = " "
        if 'boardgamemechanic' in  json_object['boardgames']['boardgame']:
            mechanic_object = json_object['boardgames']['boardgame']['boardgamemechanic']
            for obj in mechanic_object:
                try:
                    mechanic += obj['#text']+ ", "
                except:
                    mechanic = json_object['boardgames']['boardgame']['boardgamemechanic']['#text']

            mechanic_length = len(mechanic)
            mechanic = mechanic[0:mechanic_length-2]
        # Sets Rank
        bgg_rating =  json_object['boardgames']['boardgame']['statistics']['ratings']['average']
        
        # Voters
        bgg_rank_voters =  json_object['boardgames']['boardgame']['statistics']['ratings']['usersrated']

        # BGG Rating (Ratings in different categories)
        
        # Preferred Players        

        year_published = json_object['boardgames']['boardgame']['yearpublished']
        minplayers = json_object['boardgames']['boardgame']['minplayers']
        maxplayers = json_object['boardgames']['boardgame']['maxplayers']
        playingtime = json_object['boardgames']['boardgame']['playingtime']
        age = json_object['boardgames']['boardgame']['age']
        description = json_object['boardgames']['boardgame']['description']
        
        if 'thumbnail' in  json_object['boardgames']['boardgame']:
            thumbnail = json_object['boardgames']['boardgame']['thumbnail']
        else:
            thumbnail = " "

        if 'image' in json_object['boardgames']['boardgame']:
            image = json_object['boardgames']['boardgame']['image']
        else:
            image = " "
        #print(json_object['boardgames']['boardgame']['image']['poll']['results']['result']['@numvotes'])

        # Update the game with the information
        try:
            gameJson = {
                "bgg_rank_voters": int(float(bgg_rank_voters)),
                "bgg_rating": round(int(float(bgg_rating))),
                "category": str(category),
                "mechanic": str(mechanic),
                "title": title,
                "year_published": year_published,
                "minplayers": minplayers,
                "maxplayers": maxplayers,
                "playtime": playingtime,
                "age": age,
                "description": description,
                "thumbnail_url": thumbnail,
                "image_url": image
                }

            #data_dict = ast.literal_eval(json.dumps(gameJson))

            #print(data_dict)
            url = "http://zhaho.com/gathering/app/api/"+object_id
            response = requests.put(url,data=json.dumps(gameJson), headers=headers,timeout=5)

            if(response.status_code == 200):
                print(object_id+" Updated")
            else:
                print('ERROR (status_code '+str(response.status_code)+') Failed to update game_obj: '+object_id)
                print(json.dumps(gameJson))
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)
        
        # Wait in order to not overuse the API
        time.sleep(2)


# Get list of games from DB
games_obj_in_db = requests.get('https://zhaho.com/gathering/app/games/get_obj_without_data')
games = games_obj_in_db.json()


logging.info('Populating games without data:')
push_data(games)
if len(str(games)) > 2:
    logging.info('Successfully updated games')
else:
    logging.info('No games to update')
# Get list of games from DB
# games_obj_in_db = requests.get('https://zhaho.com/gathering/app/games/get_all_obj')
# games = games_obj_in_db.json()

# print('Populating games with old data:')
# push_data(games)