from django import forms
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import User, Watchlist, Bids, Address, Category, Listings, Comments
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, Column
from django.forms import ModelForm


class AddAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('addresse_name', 'address', 'shipping_add', 'billing_add', 'default_shipping', 'default_billing', 'country', 'zipcode')
        exclude = ('username',)

    def __init__(self, *args, **kwargs):
        super(AddAddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'add_address_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:add_address')
        self.helper.add_input(Submit('submit', 'Add Address', css_class="btn btn_primary", onclick="return confirm('Please Confirm to add!');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('addresse_name', placeholder="Name of Addresse")),
            Div(Field('address', placeholder="The Address")),
            Div(Field('zipcode', placeholder="Zip Code")),
            Div(Field('country', placeholder="Country")),
            Row(
                Div(Field('shipping_add', placeholder="Is this a shipping address?"), css_class="mr-4"),
                Div(Field('default_shipping', placeholder="Use this as the default shipping address?"))
                ),
            Row(
                Div(Field('billing_add', placeholder="Is this a Billing Address?"), css_class="mr-4"),
                Div(Field('default_billing', placeholder="Use this as the defaultbilling Address?"))
            )
        )

    def clean(self):
        super(AddAddressForm, self).clean()

        if self.cleaned_data.get('default_shipping') and not self.cleaned_data.get('shipping_add'):
            self._errors['default_shipping'] = self.error_class([
                'This address can only be the defaul shipping address if it is also a shipping address.'])

        if self.cleaned_data.get('default_billing') and not self.cleaned_data.get('billing_add'):
            self._errors['default_billing'] = self.error_class([
                'This address can only be the defaul billing address if it is also a billing address.'])

        return self.cleaned_data

class AmendAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('addresse_name', 'address', 'shipping_add', 'billing_add', 'default_shipping', 'default_billing', 'country', 'zipcode')
        exclude = ('username',)

    def __init__(self, *args, **kwargs):
        super(AmendAddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'amend_address_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:amend_address')
        self.helper.add_input(Submit('submit', 'Amend Address', css_class="btn btn_primary", onclick="return confirm('Please Confirm to amend!');"))
        self.helper.add_input(Submit('delete', 'Delete Address', css_class="btn btn_primary", formnovalidate='formnovalidate', onclick="return confirm('Please Confirm to Delete');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('addresse_name', placeholder="Name of Addresse")),
            Div(Field('address', placeholder="The Address")),
            Div(Field('zipcode', placeholder="Zip Code")),
            Div(Field('country', placeholder="Country")),
            Row(
                Div(Field('shipping_add', placeholder="Is this a shipping address?"), css_class="mr-4"),
                Div(Field('default_shipping', placeholder="Use this as the default shipping address?")),

                ),
            Row(
                Div(Field('billing_add', placeholder="Is this a Billing Address?"), css_class="mr-4"),
                Div(Field('default_billing', placeholder="Use this as the default billing Address?"))
            )
        )

    def clean(self):
        super(AmendAddressForm, self).clean()

        if self.cleaned_data.get('default_shipping') and not self.cleaned_data.get('shipping_add'):
            self._errors['default_shipping'] = self.error_class([
                'This address can only be the defaul shipping address if it is also a shipping address.'])

        if self.cleaned_data.get('default_billing') and not self.cleaned_data.get('billing_add'):
            self._errors['default_billing'] = self.error_class([
                'This address can only be the defaul billing address if it is also a billing address.'])

        return self.cleaned_data

class CreateAListingForm(forms.ModelForm):

    class Meta:
        model = Listings
        fields = ('title', 'short_desc', 'details', 'startingprice', 'publish', 'categories', 'pic_url')
        exclude = ( 'seller', 'publish_ts', 'closed')

    def __init__(self, *args, **kwargs):
        super(CreateAListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'create_a_listing_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:create_a_listing')
        self.helper.add_input(Submit('submit', 'Create Listing', css_class="btn btn_primary", onclick="return confirm('Please Confirm add listing!');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('title', placeholder="Listing Title")),
            Div(Field('short_desc', placeholder="Short Desc")),
            Div(Field('details', placeholder="details")),
            Div(Field('startingprice', placeholder="Price")),
            Div(Field('publish', placeholder="Publish?")),
            Div(Field('categories', placeholder="Category")),
            Div(Field('pic_url', placeholder="Picture URL"))
        )
        self.fields['categories'].help_text = "To select multiple categories, Plese press the 'cmd' key on MacOS or 'ctrl' on Windows and click selections."

class AmendAListingForm(forms.ModelForm):

    class Meta:
        model = Listings
        fields = ('title', 'short_desc', 'details', 'startingprice', 'publish', 'categories', 'closed', 'pic_url')
        exclude = ('seller', 'publish_ts')

    def __init__(self, *args, **kwargs):
        super(AmendAListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'amend_a_listing_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:amend_a_listing')
        self.helper.add_input(Submit('submit', 'Amend Listing', css_class="btn btn_primary", onclick="return confirm('Please Confirm amanedment!');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('title', placeholder="Listing Title")),
            Div(Field('short_desc', placeholder="Short Desc")),
            Div(Field('details', placeholder="details")),
            Div(Field('startingprice', placeholder="Price")),
            Div(Field('publish', placeholder="Publish?")),
            Div(Field('categories', placeholder="Category")),
            Div(Field('closed', palceholder='Close?')),
            Div(Field('pic_url', placeholder="Picture URL"))
        )
        self.fields['categories'].help_text = "To select multiple categories, Plese press the 'cmd' key on MacOS or 'ctrl' on Windows and click selections."
        self.fields['closed'].help_text = "If you close the bidding here, there will be no winners"

    def clean_categories(self):
        category_list = []

        for cat in self.cleaned_data['categories']:
            cat_id = Category.objects.get(category=cat).id
            category_list.append(cat_id)

        return category_list

class PostCommentForm(forms.ModelForm):

        class Meta:
            model = Comments
            fields = ( 'comment_title', 'comment', 'rating')
            exclude = ( 'commenting_user', 'commenting_item' )

        def __init__(self, *args, **kwargs):
            super(PostCommentForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_id = 'add_comment_form'
            self.helper.form_method = 'post'
            self.helper.form_action = reverse('auctions:post_comment')
            self.helper.add_input(Submit('submit', 'Post Comment', css_class="btn btn_primary", onclick="return confirm('Please Confirm you want to post?');"))
            self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
            self.helper.layout = Layout(
                Row(
                    Div(Field('comment_title', placeholder="Title"), css_class='form-group col mr-2'),
                    Div(Field('rating', placeholder="Star Rating"), css_class='form-group col mr-2')
                ),
                Div(Field('comment', placeholder="Your Comment"))
            )

class CloseBiddingForm(forms.ModelForm):

    class Meta:
        model = Bids
        fields = (  'bid_accepted',)
        exclude = ( 'bidamt', 'list_item', 'bidder', 'withdrawn', 'notify_email' )

    def __init__(self, *args, **kwargs):
        super(CloseBiddingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'close_bidding_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:close_bidding')
        self.helper.add_input(Submit('submit', 'Accept and/or Close Bid', css_class="btn btn_primary", onclick="return confirm('Please Confirm to you want close bidding!');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('bid_accepted', placeholder="Bid Accepted", disabled=True))
        )

class MakeABidForm(forms.ModelForm):

    class Meta:
        model = Bids
        fields = ( 'bidamt', 'notify_email', "ship_to", "bill_to" )
        exclude = ( 'list_item', 'bid_accepted', 'withdrawn', 'bidder' )

    def __init__(self, *args, **kwargs):
        max_bidamt = kwargs.pop('max_bidamt', 0)
        bidding_user = kwargs.pop('bidding_user', 0)
        print(f"max_bid and bidding_user param: {max_bidamt} {bidding_user}")
        super(MakeABidForm, self).__init__(*args, **kwargs)
        self.fields['ship_to'].queryset = Address.objects.filter(shipping_add=True).filter(username=bidding_user)
        self.fields['bill_to'].queryset = Address.objects.filter(billing_add=True).filter(username=bidding_user)
        self.fields['bidamt'].widget.attrs['min'] = max_bidamt
        self.helper = FormHelper()
        self.helper.form_id = 'make_a_bid_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:make_a_bid')
        self.helper.add_input(Submit('submit', 'Submit Bid', css_class="btn btn_primary", onclick="return confirm('Please Confirm to you want to make this bid');"))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class="btn btn_primary", formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Row(
                Div(Field('bidamt', placeholder='Bid Amount'), css_class="mr-4"),
                Div(Field('notify_email', placeholder='Notification Email'), css_class="mr-4")
                ),
            Row(
                Div(Field('ship_to', placeholder = "Address to Ship To"), css_class="mr-4"),
                Div(Field("bill_to", placeholder = "Address to Bill To"), css_class="mr-4")
                )
        )

class CreateWatchForm(forms.ModelForm):

    class Meta:
        model = Watchlist
        fields = ( 'notify_email', )
        exclude = ( 'item', 'watcher' )

    def __init__(self, *args, **kwargs):
        super(CreateWatchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'create_watch_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:add_watch')
        self.helper.add_input(Submit('submit', 'Start Watching', css_class='btn btn_primary'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn btn-primary', formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('notify_email', placeholder='Notification Email'))
        )

class DeleteWatchForm(forms.ModelForm):

    class Meta:
        model = Watchlist
        fields = ( 'id', 'notify_email' )
        exclude = ( 'item', 'watcher' )

    def __init__(self, *args, **kwargs):
        super(DeleteWatchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'delete_watch_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:remove_watch')
        self.helper.add_input(Submit('submit', 'Confirm To Remove?', css_class='btn btn_danger', formnovalidate='formnovalidate'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn btn-primary', formnovalidate='formnovalidate'))
        self.helper.layout = Layout(
            Div(Field('notify_email', placeholder='Notification Email', disabled=True))
        )


class LoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ("username", "password")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'login_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:login')
        self.helper.add_input(Submit('submit', 'Login', css_class='btn_primary'))
        self.helper.layout = Layout(
            Div(Field('username', placeholder='Login ID')),
            Div(Field('password', placeholder='Password'))
        )
        for field in self.fields:
            self.fields[field].label = False


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'registration_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:register')
        self.helper.add_input(Submit('submit', 'Register Me', css_class='btn_primary'))
        self.helper.layout = Layout(
            Div(Field('username', placeholder='Username')),
            Div(Field('email', placeholder='E-mail')),
            Div(Field('first_name', placeholder='First Name')),
            Div(Field('last_name', placeholder='Last Name')),
            Div(Field('password1', placeholder='Password')),
            Div(Field('password2', placeholder='Confirm Password'))
        )
        for field in self.fields:
            self.fields[field].label = False


    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ChangePasswordForm(PasswordChangeForm):

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'changepassword_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('auctions:change_password')
        self.helper.add_input(Submit('submit', 'Change Password', css_class='btn_primary'))
        self.helper.layout = Layout(
            Div(Field('old_password', placeholder='Old Password')),
            Div(Field('new_password1', placeholder='New Password')),
            Div(Field('new_password2', placeholder='Confirm Passowrd'))
        )
        for field in self.fields:
            self.fields[field].label = False
