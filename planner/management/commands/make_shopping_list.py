from planner.services.shopping_list_generator import generate_shopping_list
from django.core.management.base import BaseCommand
import argparse

class Command(BaseCommand):
    help = 'Generate a shopping list'

    def handle(self, *args, **kwargs):
        shopping_list = generate_shopping_list(args.recipes)
        self.stdout.write(shopping_list.model_dump_json(indent=2))



# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a shopping list')
    parser.add_argument(
        '--recipes',
        required=True,
        help='Comma-separated list of recipe IDs (e.g., 1,2,3)',
        type=lambda x: [int(s.strip()) for s in x.split(',')]
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    shopping_list = generate_shopping_list(args.recipes)
    return shopping_list

if __name__ == "__main__":
    shopping_list = main()
    print(shopping_list.model_dump_json(indent=2))




