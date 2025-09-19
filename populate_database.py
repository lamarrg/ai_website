from database import db_session, init_db
from site_content.sample_class import SampleClass

# Initialize the database
init_db()

# Define content for each page
pages_content = {
        'resources': {
        'name': 'Resources',
        'url': '/resources',
        'description': 'Access a wealth of resources to help you make informed decisions. UNIQUE_ITEM: ResourceHub3000'
    },
        'contact': {
        'name': 'Contact',
        'url': '/resources',
        'description': 'The page with the contact form to send a message to the company. UNIQUE_ITEM: HawkDive3000'
    },
    'about': {
        'name': 'About Website',
        'url': '/about',
        'description': 'Learn about our mission to provide transparent and accessible services. UNIQUE_ITEM: PeopleAccess1000'
    }
}

# Populate the database
for page, content in pages_content.items():
    sample = SampleClass(name=content['name'], description=content['description'], url=content['url'])
    db_session.add(sample)

db_session.commit()

print("Database populated successfully!")
