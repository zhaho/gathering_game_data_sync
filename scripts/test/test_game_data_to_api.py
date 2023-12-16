from game_data_to_api import game_info

#game = game_info("63706")
game = game_info("116954")

print("\nValidating game: " + game.title())
print("\nCategories: "+game.category())
print("\nMechanics: "+game.mechanic())

def test_valid():
    assert game.is_valid() == True
        
def test_titles():
    assert len(game.title()) > 0
    assert type(game.title()) == str

def test_categories():
    assert len(game.category()) > 0
    assert type(game.category()) == str

def test_mechanics():
    assert len(game.mechanic()) > 0
    assert type(game.mechanic()) == str

def test_bgg_rating():
    assert len(str(game.bgg_rating())) > 0
    assert type(game.bgg_rating()) == int


