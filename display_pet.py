from PIL import Image
#pip install pillow
class DisplayPet:

    #pet will have 4 levels of hunger; start as 0, goes to 3 when starved
    hunger = 0
    #this will eventually become an array of actual images to send.
    image_array = ["images/pet_test/pet_test_0.png", "images/pet_test/pet_test_1.png", "images/pet_test/pet_test_2.png", "images/pet_test/pet_test_3.png"]

    def __init__(self):
        pass

    #increase or decrease hunger from function calls
    def hunger_increase(self):
        self.hunger = min(3, self.hunger + 1)
        return

    def hunger_decrease(self):
        self.hunger = max(0, self.hunger - 1)
        return

    # need function that sends image dependent on hunger
    # need function to swap image array on pet type change

    def display(self):
        return self.image_array[self.hunger]