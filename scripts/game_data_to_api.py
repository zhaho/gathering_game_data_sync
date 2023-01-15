import xmltodict, json, requests, time, logging, re
import xml.etree.ElementTree as ET

# Logging configuration
logging.basicConfig(filename='/var/log/bgg.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

class game_info:
    def __init__(self, object_id):
        self.object_id = object_id
        self.response = requests.get("https://boardgamegeek.com/xmlapi/boardgame/"+self.object_id+"?stats=1") # Get information of game through BGG API
        self.dictionary = xmltodict.parse(self.response.content) # Parse the XML to Dict
        self.json_object_string = json.dumps(self.dictionary) # Convert to String
        self.json_object = json.loads(self.json_object_string) # Convert JSON to LIST
       
    def title(self):
        title_object = self.json_object['boardgames']['boardgame']['name']

        for obj in title_object:
            try:
                obj_len = len(obj.keys())
            except:
                title = self.json_object['boardgames']['boardgame']['name']['#text']
                obj_len = 0
           
            if obj_len > 2:
                title = obj['#text']
        
        return title

    def category(self):
        # Sets the category
        category = " "
        if 'boardgamecategory' in  self.json_object['boardgames']['boardgame']:
            category_object = self.json_object['boardgames']['boardgame']['boardgamecategory']
            for obj in category_object:
                try:
                    category += obj['#text']+ ", "
                except:
                    category = self.json_object['boardgames']['boardgame']['boardgamecategory']['#text']

            category_length = len(category)
            return str(category[0:category_length-2])

    def mechanic(self):
        # Sets the mechanic
        mechanic = " "
        if 'boardgamemechanic' in  self.json_object['boardgames']['boardgame']:
            mechanic_object = self.json_object['boardgames']['boardgame']['boardgamemechanic']
            for obj in mechanic_object:
                try:
                    mechanic += obj['#text']+ ", "
                except:
                    mechanic = self.json_object['boardgames']['boardgame']['boardgamemechanic']['#text']

            mechanic_length = len(mechanic)
            return str(mechanic[0:mechanic_length-2])

    def bgg_rating(self):
        # Sets Rank
        return round(int(float(self.json_object['boardgames']['boardgame']['statistics']['ratings']['average'])))

    def bgg_rank_voters(self):
        # Voters
        return int(float(self.json_object['boardgames']['boardgame']['statistics']['ratings']['usersrated']))

    def year_published(self):
        return self.json_object['boardgames']['boardgame']['yearpublished']
    
    def minplayers(self):
        return self.json_object['boardgames']['boardgame']['minplayers']
    
    def maxplayers(self):
        return self.json_object['boardgames']['boardgame']['maxplayers']
    
    def playtime(self):
        return self.json_object['boardgames']['boardgame']['playingtime']

    def age(self):
        return self.json_object['boardgames']['boardgame']['age']
    
    def description(self):
        return self.json_object['boardgames']['boardgame']['description']

    def image(self):
        if 'image' in self.json_object['boardgames']['boardgame']:
            image = self.json_object['boardgames']['boardgame']['image']
        else:
            image = " "
        return image

    def thumbnail(self):
        if 'thumbnail' in  self.json_object['boardgames']['boardgame']:
            thumbnail = self.json_object['boardgames']['boardgame']['thumbnail']
        else:
            thumbnail = " "
        return thumbnail

    def preferred_players(self):

        url = 'https://api.geekdo.com/xmlapi/boardgame/'+str(self.object_id)

        response = requests.get(url)
        root = ET.fromstring(response.content)

        best_numplayers = 0
        highest_value = 0    
        for item in root.findall('./boardgame/poll[@name="suggested_numplayers"]/results'):
            numplayers = re.sub("[^0-9]", "", item.attrib['numplayers'])
            best = int(item.find('./result[@value="Best"]').attrib['numvotes'])
            if best > highest_value:
                highest_value = best
                best_numplayers = numplayers


        if best_numplayers == 0:
            best_numplayers = 0
            highest_value = 0
            for item in root.findall('./boardgame/poll[@name="suggested_numplayers"]/results'):
                numplayers = re.sub("[^0-9]", "", item.attrib['numplayers'])
                best = int(item.find('./result[@value="Recommended"]').attrib['numvotes'])
                if best > highest_value:
                    highest_value = best
                    best_numplayers = numplayers


        return int(best_numplayers)
    
    def is_valid(self):
        try:
            if self.json_object['boardgames']['boardgame']['error']:
                return False
            return True
        except:
            return True
        

def update_games(api_url):
    # Set headers for post
    headers = {"Content-Type": "application/json"}

    # Fetch games to update
    games_obj_in_db = requests.get(api_url)
    games = games_obj_in_db.json()

    logging.info('Game that needs update: '+ str(len(games)))

    # Loop the objects in JSON
    for obj in games:
        game = game_info(obj['object_id'])
        object_id = obj['object_id']

        if game.is_valid():


            # Prepare JSON Payload
            gameJson = {
                    "bgg_rank_voters": game.bgg_rank_voters(),
                    "bgg_rating": game.bgg_rating(),
                    "category": game.category(),
                    "mechanic": game.mechanic(),
                    "title": game.title(),
                    "year_published": game.year_published(),
                    "minplayers": game.minplayers(),
                    "maxplayers": game.maxplayers(),
                    "preferred_players": game.preferred_players(),
                    "playtime": game.playtime(),
                    "age": game.age(),
                    "description": game.description(),
                    "thumbnail_url": game.thumbnail(),
                    "image_url": game.image()
                    }

            print(object_id,' is best on: ',game.preferred_players())
            # Send information to API
            try:
                url = "http://zhaho.com/gathering/app/api/"+object_id
                response = requests.put(url,data=json.dumps(gameJson), headers=headers,timeout=5)
                if(response.status_code == 200):
                    logging.info(game.title() + ' successfully updated')
                else:
                    logging.error(game.title() + ' failed to update. status_code: '+str(response.status_code))
            except requests.exceptions.HTTPError as errh:
                logging.error(errh)
            except requests.exceptions.ConnectionError as errc:
                logging.error(errc)
            except requests.exceptions.Timeout as errt:
                logging.error(errt)
            except requests.exceptions.RequestException as err:
                logging.error(err)
            
            # Wait in order to not overuse the API
            time.sleep(2)
        
        else:
            logging.info('No data from current game - Skipping')


        if len(str(games)) > 2:
            logging.info('Successfully updated games')
        else:
            logging.info('No games to update')


update_games('https://zhaho.com/gathering/app/games/get_obj_without_data')


