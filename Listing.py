class Listing:
    def __init__(self, id, title, price, path, nb_bedrooms, property_type, seller_name):
        self.id = id
        self.title = title
        self.price = price
        self.path = path
        self.nb_bedrooms = nb_bedrooms
        self.property_type = property_type
        self.seller_name = seller_name
        
            
    def toString(self):
        return f"Listing(id= {self.id}, title= {self.title}, price= {self.price}, link= {self.path})"
    





    