from django.contrib.auth.models import User
from plattform.models import Profile
import string
import random

def get_random_image():
    def name_generator(size=9, chars=string.ascii_uppercase + string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    # Get the current working directory
    base_dir = os.getcwd()

    url = "https://random.imagecdn.app/500/500"
    img_data = requests.get(url).content
    random_name = name_generator() + '.jpg'
    file_location = os.path.join(base_dir, 'media', 'profile_pics', random_name)

    with open(file_location, 'wb') as handler:
        handler.write(img_data)

    result = "profile_pics/" + random_name
    print(result)
    return result


user=()
