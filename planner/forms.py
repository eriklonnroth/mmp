from django import forms


class CreateRecipeForm(forms.Form):
    dish_idea = forms.CharField(
        label="What would you like to cook?",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Vegetarian lasagna, Chocolate brownies, Healthy salad...',
            'class': 'form-field'
        })
    )
    
    notes = forms.CharField(
        label="Recipe notes (optional)",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Not too spicy, Air fryer-friendly, Keep it simple...',
            'class': 'form-field'
        })
    )
    
    dietary_preferences = forms.CharField(
        label="Dietary Preferences (optional)",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Vegan, Gluten-free, Low-carb...',
            'class': 'form-field'
        })
    )
    
    servings = forms.IntegerField(
        label="Servings",
        min_value=1,
        max_value=12,
        initial=4,
        widget=forms.Select(
            choices=[(i, f"{i} serving{'s' if i > 1 else ''}") for i in range(1, 11)],
            attrs={
                'class': 'form-field'
            }
        )
    )
    
    units = forms.ChoiceField(
        label="Measurement Units",
        choices=[
            ('metric', 'Metric (g, ml, °C)'),
            ('us', 'US (oz, cups, °F)')
        ],
        initial='metric',
        widget=forms.Select(attrs={
            'class': 'form-field'
        })
    )