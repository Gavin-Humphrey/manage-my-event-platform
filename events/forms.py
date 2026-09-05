import os
from django import forms
from django.core.files.storage import default_storage
from .models import Event, RSVP, RSVPGuest


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            files_list = files.getlist(name)
            return files_list if files_list else super().value_from_datadict(data, files, name)
        return super().value_from_datadict(data, files, name)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'accept': 'image/*', 'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            cleaned_list = []
            for item in data:
                if item:
                    cleaned_list.append(single_file_clean(item, initial))
            return cleaned_list
        return single_file_clean(data, initial)


class EventForm(forms.ModelForm):
    PAGE_BG_CHOICES = [
        # Neutrals
        ('#f8fafc', 'Slate Light (Default)'),
        ('#ffffff', 'Pure White'),
        ('#f1f5f9', 'Cool Gray'),
        ('#f5f5f4', 'Warm Stone'),
        ('#fafaf9', 'Soft Ivory'),

        # Dark
        ('#0f172a', 'Dark Slate'),
        ('#1e293b', 'Deep Blue Gray'),
        ('#18181b', 'Charcoal'),
        ('#292524', 'Dark Stone'),
        ('#071C13', 'Emerald Dark'),
        ('#0B2B1D', 'Deep Emerald'),

        # Warm
        ('#fffbeb', 'Warm Cream'),
        ('#fef3c7', 'Soft Amber'),
        ('#fff7ed', 'Peach Cream'),
        ('#fdf2f8', 'Blush'),
        ('#fff1f2', 'Soft Rose'),

        # Gold / Luxury
        ('#E8D3A7', 'Light Gold'),
        ('#F7EED7', 'Soft Champagne'),
        ('#F5E9CC', 'Pale Gold'),
        ('#FAF3E0', 'Champagne Cream'),

        # Cool / Fresh
        ('#ecfdf5', 'Soft Emerald'),
        ('#f0fdf4', 'Mint'),
        ('#eff6ff', 'Soft Blue'),
        ('#f0f9ff', 'Soft Sky'),
        ('#eef2ff', 'Soft Indigo'),
        ('#f5f3ff', 'Soft Violet'),

        # Elegant
        ('#faf5ff', 'Lavender'),
        ('#fdf4ff', 'Soft Fuchsia'),
        ('#fce7f3', 'Elegant Pink'),
        ('#f3e8ff', 'Soft Purple'),
    ]

    SECTION_BG_CHOICES = [
        # Neutrals
        ('#ffffff', 'White Card (Default)'),
        ('#f8fafc', 'Slate White Card'),
        ('#f1f5f9', 'Light Gray Card'),
        ('#f5f5f4', 'Warm Stone Card'),
        ('#fafaf9', 'Ivory Card'),

        # Dark
        ('#1e293b', 'Dark Slate Card'),
        ('#0f172a', 'Midnight Card'),
        ('#27272a', 'Charcoal Card'),
        ('#0B2B1D', 'Deep Emerald Card'),
        ('#071C13', 'Emerald Dark Card'),

        # Warm
        ('#fef3c7', 'Warm Amber Card'),
        ('#ffedd5', 'Peach Card'),
        ('#ffe4e6', 'Soft Rose Card'),
        ('#fce7f3', 'Blush Pink Card'),

        # Gold / Metallic / Luxury
        ('#78350f', 'Deep Gold Brown'),
        ('#92400e', 'Burnt Amber'),
        ('#FFF8E1', 'Champagne Gold'),
        ('#F5E6B3', 'Pale Gold'),
        ('#E8D3A7', 'Light Gold'),
        ('#D4AF37', 'Classic Gold'),
        ('#C5A059', 'Real Gold'),
        ('#B08C46', 'Antique Gold'),
        ('#A38241', 'Dark Gold'),
        ('#8C6A2D', 'Deep Gold'),
        ('#6F531F', 'Dark Metallic Gold'),
        ('#4A3513', 'Rich Dark Gold'),

        # Emerald / Green
        ('#dcfce7', 'Soft Emerald Card'),
        ('#d1fae5', 'Mint Card'),
        ('#d9f2e6', 'Pale Emerald Card'),

        # Cool / Fresh
        ('#dbeafe', 'Soft Blue Card'),
        ('#e0f2fe', 'Sky Blue Card'),
        ('#e0e7ff', 'Soft Indigo Card'),
        ('#ede9fe', 'Soft Violet Card'),

        # Elegant
        ('#f3e8ff', 'Lavender Card'),
        ('#fae8ff', 'Soft Fuchsia Card'),
    ]

    BODY_COLOR_CHOICES = [
        # Neutrals
        ('#475569', 'Standard Slate (Default)'),
        ('#334155', 'Darker Slate'),
        ('#64748b', 'Medium Slate'),
        ('#52525b', 'Zinc Gray'),
        ('#44403c', 'Warm Gray'),
        ('#1e293b', 'Deep Slate'),

        # Emerald / Green
        ('#0B2B1D', 'Deep Emerald'),
        ('#14532d', 'Forest Green'),
        ('#166534', 'Deep Green'),
        ('#047857', 'Emerald'),
        ('#15803d', 'Green'),

        # Gold / Earth
        ('#78350f', 'Deep Gold Brown'),
        ('#92400e', 'Burnt Amber'),
        ('#FFF8E1', 'Champagne Gold'),
        ('#F5E6B3', 'Pale Gold'),
        ('#E8D3A7', 'Light Gold'),
        ('#D4AF37', 'Classic Gold'),
        ('#C5A059', 'Real Gold'),
        ('#B08C46', 'Antique Gold'),
        ('#A38241', 'Dark Gold'),
        ('#8C6A2D', 'Deep Gold'),
        ('#6F531F', 'Dark Metallic Gold'),
        ('#4A3513', 'Rich Dark Gold'),

        # Blues
        ('#2B5B84', 'Steel Blue'),
        ('#1e40af', 'Blue'),
        ('#1d4ed8', 'Royal Blue'),
        ('#3730a3', 'Indigo'),
        ('#4338ca', 'Deep Indigo'),

        # Warm
        ('#9a3412', 'Burnt Orange'),
        ('#b45309', 'Amber'),
        ('#991b1b', 'Deep Red'),
        ('#be123c', 'Rose'),

        # Purple
        ('#7e22ce', 'Purple'),
        ('#86198f', 'Magenta'),

        # Light — useful with dark backgrounds
        ('#94a3b8', 'Light Gray'),
        ('#cbd5e1', 'Soft Gray'),
        ('#e2e8f0', 'Off-White'),
        ('#f1f5f9', 'Very Light Gray'),
        ('#ffffff', 'Pure White'),
    ]

    MUTED_COLOR_CHOICES = [
        # Slate / Gray
        ('#94a3b8', 'Slate Muted (Default)'),
        ('#64748b', 'Medium Slate'),
        ('#6b7280', 'Neutral Gray'),
        ('#71717a', 'Zinc Gray'),
        ('#78716c', 'Warm Gray'),
        ('#475569', 'Dark Slate'),
        ('#334155', 'Deep Slate'),

        # Emerald / Green
        ('#527565', 'Muted Emerald'),
        ('#4d8068', 'Soft Emerald'),
        ('#6b8f7a', 'Sage Green'),

        # Gold / Earth
        ('#A38241', 'Dark Gold'),
        ('#B08C46', 'Antique Gold'),
        ('#9C8450', 'Muted Gold'),
        ('#8B7355', 'Warm Bronze'),

        # Light
        ('#cbd5e1', 'Soft Light Gray'),
        ('#d1d5db', 'Light Gray'),
        ('#e2e8f0', 'Pale Slate'),
        ('#f1f5f9', 'Very Light'),
        ('#f8fafc', 'Slate White'),
        ('#ffffff', 'Pure White'),

        # Colored Muted
        ('#4f46e5', 'Muted Indigo'),
        ('#047857', 'Muted Emerald'),
        ('#b45309', 'Muted Amber'),
        ('#be123c', 'Muted Rose'),
        ('#7e22ce', 'Muted Purple'),
        ('#2B5B84', 'Muted Steel Blue'),
    ]

    HEADING_COLOR_CHOICES = [
        # Neutrals / Slate
        ('#0f172a', 'Dark Slate (Default)'),
        ('#1e293b', 'Deep Slate'),
        ('#334155', 'Slate'),
        ('#18181b', 'Charcoal'),
        ('#000000', 'Pure Black'),

        # Emerald / Green
        ('#0B2B1D', 'Deep Emerald'),
        ('#071C13', 'Emerald Dark'),
        ('#14532d', 'Forest Green'),
        ('#166534', 'Deep Green'),
        ('#047857', 'Emerald'),

        # Gold / Earth
        ('#78350f', 'Deep Gold Brown'),
        ('#92400e', 'Burnt Amber'),
        ('#FFF8E1', 'Champagne Gold'),
        ('#F5E6B3', 'Pale Gold'),
        ('#E8D3A7', 'Light Gold'),
        ('#D4AF37', 'Classic Gold'),
        ('#C5A059', 'Real Gold'),
        ('#B08C46', 'Antique Gold'),
        ('#A38241', 'Dark Gold'),
        ('#8C6A2D', 'Deep Gold'),
        ('#6F531F', 'Dark Metallic Gold'),
        ('#4A3513', 'Rich Dark Gold'),

        # Blues
        ('#1e3a8a', 'Deep Blue'),
        ('#1e40af', 'Dark Blue'),
        ('#1d4ed8', 'Royal Blue'),
        ('#2B5B84', 'Steel Blue'),
        ('#312e81', 'Deep Indigo'),

        # Warm & Accent
        ('#9a3412', 'Burnt Orange'),
        ('#b45309', 'Warm Amber'),
        ('#991b1b', 'Deep Red'),
        ('#7f1d1d', 'Deep Crimson'),
        ('#be123c', 'Deep Rose'),

        # Purple
        ('#581c87', 'Deep Purple'),
        ('#7e22ce', 'Purple'),

        # Light — for dark backgrounds
        ('#f8fafc', 'Soft White'),
        ('#ffffff', 'Pure White'),
        ('#e2e8f0', 'Off-White'),
        ('#cbd5e1', 'Light Gray'),
    ]

    hero_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    
    gallery_files = MultipleFileField(required=False)

    theme_color = forms.CharField(
        required=False,
        initial='#3b82f6',
        widget=forms.TextInput(attrs={'type': 'color'})
    )

    page_bg_color = forms.ChoiceField(
        choices=PAGE_BG_CHOICES,
        required=False,
        initial='#f8fafc'
    )

    section_bg_color = forms.ChoiceField(
        choices=SECTION_BG_CHOICES,
        required=False,
        initial='#ffffff'
    )

    heading_color = forms.ChoiceField(
        choices=HEADING_COLOR_CHOICES,
        required=False,
        initial='#0f172a'
    )

    body_color = forms.ChoiceField(
        choices=BODY_COLOR_CHOICES,
        required=False,
        initial='#475569'
    )

    muted_color = forms.ChoiceField(
        choices=MUTED_COLOR_CHOICES,
        required=False,
        initial='#94a3b8'
    )

    font_family = forms.ChoiceField(
        choices=[
            ('sans-serif', 'Sans-Serif (Modern / Clean)'),
            ('serif', 'Serif (Classic / Elegant)'),
            ('mono', 'Monospace (Minimal / Tech)'),
        ],
        required=False,
        initial='sans-serif'
    )

    layout_style = forms.ChoiceField(
        choices=[
            ('centered', 'Centered Hero Card'),
            ('split', 'Split Two-Column Layout'),
            ('minimal', 'Minimalist Clean'),
        ],
        required=False,
        initial='centered'
    )

    show_about_section = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500 cursor-pointer'
        })
    )

    # about_title = forms.CharField(
    #     required=False,
    #     initial="About the Host",
    #     max_length=100,
    #     widget=forms.TextInput(attrs={
    #         'class': 'w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500'
    #     })
    # )
    guest_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        help_text="Write a short bio or background text about the host/celebrant."
    )

    allow_guest_messages = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500 cursor-pointer'
        }),
        help_text="Allow guests to leave a special message for the celebrant."
    )

    class Meta:
        model = Event
        fields = [
            'title', 'event_date', 'location_name', 'address','show_about_section', 'about_title', 'about_text',
            'allow_plus_ones', 'max_plus_ones_per_guest', 'allow_guest_messages', 'enable_qr_checkins', 'theme_settings'
        ]
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.theme_settings:
            theme = self.instance.theme_settings
            self.fields['theme_color'].initial = theme.get('primary_color', '#3b82f6')
            self.fields['page_bg_color'].initial = theme.get('page_bg_color', '#f8fafc')
            self.fields['section_bg_color'].initial = theme.get('section_bg_color', '#ffffff')
            self.fields['heading_color'].initial = theme.get('heading_color', '#0f172a')
            self.fields['body_color'].initial = theme.get('body_color', '#475569')
            self.fields['muted_color'].initial = theme.get('muted_color', '#94a3b8')
            self.fields['font_family'].initial = theme.get('font_family', 'sans-serif')
            self.fields['layout_style'].initial = theme.get('layout_style', 'centered')
            self.fields['show_about_section'].initial = theme.get('show_about_section', False)
            # self.fields['about_title'].initial = theme.get('about_title', 'About the Host')
            self.fields['guest_message'].initial = theme.get('guest_message', '')
        file_classes = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'

        for name, field in self.fields.items():
            if name in ['hero_image', 'gallery_files']:
                field.widget.attrs.update({'class': file_classes})
            elif name == 'theme_color':
                field.widget.attrs.update({'class': 'h-10 w-20 p-1 border border-slate-300 rounded-lg cursor-pointer'})
            elif name == 'about_text':
                field.widget.attrs.update({'class': 'w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})
            elif name == 'about_title':
                field.widget.attrs.update({'class': 'w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})
            else:
                field.widget.attrs.update({'class': 'w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})

    def clean_gallery_files(self):
        """Validate max photo count and individual file sizes."""
        uploaded_files = self.cleaned_data.get('gallery_files') or []
        if not isinstance(uploaded_files, (list, tuple)):
            uploaded_files = [uploaded_files] if uploaded_files else []

        existing_gallery = []
        if self.instance and self.instance.pk and self.instance.theme_settings:
            existing_gallery = self.instance.theme_settings.get('gallery_images', [])

        total_photos = len(existing_gallery) + len(uploaded_files)
        if total_photos > 10:
            raise forms.ValidationError(
                f"You can have a maximum of 10 gallery photos. You currently have {len(existing_gallery)} and tried to upload {len(uploaded_files)}."
            )

        max_size_bytes = 5 * 1024 * 1024
        for f in uploaded_files:
            if hasattr(f, 'size') and f.size > max_size_bytes:
                raise forms.ValidationError(f"File '{f.name}' exceeds the maximum allowed size of 5MB.")

        return uploaded_files

    def save(self, commit=True):
            instance = super().save(commit=False)
            theme = instance.theme_settings or {}
            
            existing_gallery_urls = list(theme.get('gallery_images', []))

            hero_file = self.cleaned_data.get('hero_image')
            if hero_file:
                path = default_storage.save(f"event_heroes/{hero_file.name}", hero_file)
                theme['hero_image_url'] = f"/media/{path}"

            uploaded_gallery_files = self.cleaned_data.get('gallery_files') or []
            if not isinstance(uploaded_gallery_files, (list, tuple)):
                uploaded_gallery_files = [uploaded_gallery_files]

            for gallery_file in uploaded_gallery_files:
                if gallery_file:
                    path = default_storage.save(f"event_galleries/{gallery_file.name}", gallery_file)
                    media_path = f"/media/{path}"
                    if media_path not in existing_gallery_urls:
                        existing_gallery_urls.append(media_path)

            gallery_slides = []
            for index, url in enumerate(existing_gallery_urls):
                desc = ""
                if hasattr(self, 'data') and self.data:
                    desc = self.data.get(f'gallery_desc_{index}', '')
                else:
                    old_slides = theme.get('gallery_slides', [])
                    if index < len(old_slides):
                        desc = old_slides[index].get('description', '')

                gallery_slides.append({
                    'url': url,
                    'description': desc
                })

            theme['gallery_images'] = existing_gallery_urls
            theme['gallery_slides'] = gallery_slides
            theme['primary_color'] = self.cleaned_data.get('theme_color', '#3b82f6')
            theme['page_bg_color'] = self.cleaned_data.get('page_bg_color', '#f8fafc')
            theme['section_bg_color'] = self.cleaned_data.get('section_bg_color', '#ffffff')
            theme['heading_color'] = self.cleaned_data.get('heading_color', '#0f172a')
            theme['body_color'] = self.cleaned_data.get('body_color', '#475569')
            theme['muted_color'] = self.cleaned_data.get('muted_color', '#94a3b8')
            theme['font_family'] = self.cleaned_data.get('font_family', 'sans-serif')
            theme['layout_style'] = self.cleaned_data.get('layout_style', 'centered')
            theme['show_about_section'] = self.cleaned_data.get('show_about_section', False)
            theme['guest_message'] = self.cleaned_data.get('guest_message', '')

            # Capture organizer footer contact inputs
            existing_contacts = theme.get('organizer_contacts', {})
            theme['organizer_contacts'] = {
                'name': self.data.get('organizer_name', existing_contacts.get('name', '')) if hasattr(self, 'data') and self.data else existing_contacts.get('name', ''),
                'phone': self.data.get('organizer_phone', existing_contacts.get('phone', '')) if hasattr(self, 'data') and self.data else existing_contacts.get('phone', ''),
                'whatsapp': self.data.get('organizer_whatsapp', existing_contacts.get('whatsapp', '')) if hasattr(self, 'data') and self.data else existing_contacts.get('whatsapp', ''),
            }

            instance.theme_settings = theme
            if commit:
                instance.save()
            return instance

class RSVPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = RSVP
        fields = ['first_name', 'last_name', 'email', 'phone', 'status', 'dietary_restrictions']

class RSVPGuestForm(forms.ModelForm):
    class Meta:
        model = RSVPGuest
        fields = '__all__'  