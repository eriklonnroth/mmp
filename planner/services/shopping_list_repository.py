from django.contrib.auth.models import User
from planner.models import ShoppingList as DBShoppingList, ShoppingItem as DBShoppingItem
from .shopping_list_generator import ShoppingList

class ShoppingListRepository:
    @staticmethod
    def get_category_key(category: str):
        for cat in DBShoppingItem.CATEGORIES:
            if cat[1] == category:
                return cat[0]
        return 'non-food'

    @staticmethod
    def save_shopping_list(shopping_list: ShoppingList, user: User=None):        
        db_shopping_list = DBShoppingList.objects.create(
            name=shopping_list.name,
            user=user
        )

        for item in shopping_list.items:
            DBShoppingItem.objects.create(
                shopping_list=db_shopping_list,
                name=item.name,
                quantity=item.quantity,
                used_in=item.used_in,
                category=ShoppingListRepository.get_category_key(item.category)
            )

        return db_shopping_list

# Helper functions
def save_shopping_list_to_db(shopping_list: ShoppingList, user=None) -> DBShoppingList:
    service = ShoppingListRepository()
    return service.save_shopping_list(shopping_list, user)