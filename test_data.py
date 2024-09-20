# add_test_data.py

from app import app, db, models  # Import the existing db instance
from faker import Faker
import random

fake = Faker()

def add_test_data(num_records=100):
    with app.app_context():  # Ensure you have the app context
        brands = models.Brand.query.all()
        types = models.Type.query.all()

        for _ in range(num_records):
            new_part = models.Part()
            new_part.name = fake.catch_phrase()
            new_part.width = random.randint(1, 100)

            selected_brand = random.choice(brands)
            new_part.brands.append(selected_brand)

            selected_type = random.choice(types)
            new_part.type_id = selected_type.id

            tag_names = [fake.word() for _ in range(random.randint(1, 5))]
            for tag_name in tag_names:
                tag = models.Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    new_tag = models.Tag(name=tag_name)
                    db.session.add(new_tag)
                    db.session.commit()
                    new_part.tags.append(new_tag)
                else:
                    new_part.tags.append(tag)

            # Dummy image handling
            dummy_image_name = f"{fake.uuid4()}.jpg"
            new_image = models.Image(name=dummy_image_name)
            new_part.images.append(new_image)

            db.session.add(new_part)
            db.session.commit()

        print(f"{num_records} records added to the database.")

if __name__ == "__main__":
    add_test_data(1)  # Call the function to add data
