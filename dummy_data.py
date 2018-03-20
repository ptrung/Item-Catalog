from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Delete Categories if exisitng.
session.query(Category).delete()
# Delete Items if exisitng.
session.query(Item).delete()
# Delete Users if exisitng.
session.query(User).delete()

# User
user = User(name = "Jane Doe", email = "jane.doe@gmail.com", picture = "https://cdn.pixabay.com/photo/2016/03/31/19/57/avatar-1295406_960_720.png")
session.add(user)
session.commit()

# Category Africa
category1 = Category(name="Africa")

session.add(category1)
session.commit()


item1 = Item(title="Diddle Daddle Popcorn", description="Caramel mint flavoured caramelised popcorn",
                    category=category1, user=user)
session.add(item1)
session.commit()

item2 = Item(title="Custard creams", description="Crunchy biscuits with a creamy custard filling",
                    category=category1, user=user)
session.add(item2)
session.commit()


# Category Asia
category2 = Category(name="Asia")
session.add(category2)
session.commit()


# Category Europe
category3 = Category(name="Europe")
session.add(category3)
session.commit()

item1 = Item(title="Mr. Tom", description="Caramel Peanut bar",
                    category=category3, user=user)
session.add(item1)
session.commit()

item2 = Item(title="Thorntons Fabulous Fudge", description="Vanilla Fudge",
                    category=category3, user=user)
session.add(item2)
session.commit()

item3 = Item(title="Double Dip", description="Orange and cherry flavor",
                    category=category3, user=user)
session.add(item3)
session.commit()

item4 = Item(title="Golden eggs", description="chocolate with crunchy caramel rolled in gold",
                    category=category3, user=user)
session.add(item4)
session.commit()


# Category North America
category4 = Category(name="North America")
session.add(category4)
session.commit()

item1 = Item(title="Clark", description="Real milk chocolate - Real peanut butter crunch",
                    category=category4, user=user)
session.add(item1)
session.commit()

item2 = Item(title="Chocolate Pop Rocks", description="Chocolate covered popping candy",
                    category=category4, user=user)
session.add(item2)
session.commit()

item3 = Item(title="Bazooka", description="Original and blue razz bubble gum",
                    category=category4, user=user)
session.add(item3)
session.commit()


# Category South America
category5 = Category(name="South America")
session.add(category5)
session.commit()

item1 = Item(title="Leche y Miel", description="Milk and honey favored hard candy",
                    category=category5, user=user)
session.add(item1)
session.commit()


# Category Antarctica
category6 = Category(name="Antarctica")
session.add(category6)
session.commit()


# Category Australia
category7 = Category(name="Australia")
session.add(category7)
session.commit()

item1 = Item(title="Zappo", description="7 sour grape flavour chews",
                    category=category7, user=user)
session.add(item1)
session.commit()

print "added items!"
