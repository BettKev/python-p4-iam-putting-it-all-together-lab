import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

@pytest.fixture(scope='module')
def client():
    '''Fixture to set up a test client for Flask'''
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def user():
    '''Fixture to set up a test user'''
    user = User(username='testuser', password='password')
    db.session.add(user)
    db.session.commit()
    yield user
    # Clean up after the test
    db.session.delete(user)
    db.session.commit()

class TestRecipe:
    '''Test for Recipe model in models.py'''

    def test_has_attributes(self, user):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():
            # Delete all existing recipes
            Recipe.query.delete()
            db.session.commit()

            # Create a recipe associated with the user
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                               """ raptures building an bringing be. Elderly is detract""" + \
                               """ tedious assured private so to visited. Do travelling""" + \
                               """ companions contrasted it. Mistress strongly remember""" + \
                               """ up to. Ham him compass you proceed calling detract.""" + \
                               """ Better of always missed we person mr. September""" + \
                               """ smallness northward situation few her certainty""" + \
                               """ something.""",
                minutes_to_complete=60,
                user_id=user.id  # Associate the recipe with the user
            )

            # Add recipe to the session and commit
            db.session.add(recipe)
            db.session.commit()

            # Retrieve the recipe from the database
            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            # Assertions to check if the recipe is correctly saved
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something."""
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id  # Verify the user_id is correctly set

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            recipe = Recipe()
            
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''must raise either a sqlalchemy.exc.IntegrityError with constraints or a custom validation ValueError'''

        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol")
                db.session.add(recipe)
                db.session.commit()
