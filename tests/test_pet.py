from pet import Pet


def test_pet_keeps_name_and_type():
    pet = Pet("Biscuit", "Dog")

    assert pet.name == "Biscuit"
    assert pet.animal_type == "Dog"
