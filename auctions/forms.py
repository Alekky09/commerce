from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField(label="Listing title", max_length=64)
    description = forms.CharField(label="Description", max_length=256, widget=forms.Textarea) # This gives textarea
    starting_bid = forms.IntegerField(label="Starting bid", min_value=0)
    image_url = forms.CharField(label="Image url", max_length=512, required=False)
    category = forms.CharField(label="Category", max_length=32, required=False)

class CommentForm(forms.Form):
    comment = forms.CharField(label="", max_length=128, widget=forms.Textarea(attrs={'placeholder': 'Comment here...'}))